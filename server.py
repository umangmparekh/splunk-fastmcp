# server.py
import os
import json
import logging
from typing import List, Dict, Optional, Any
from fastmcp import FastMCP
import splunklib.client as client
import splunklib.results as results
from splunklib.binding import HTTPError


mcp = FastMCP("splunk-mcp")

logger = logging.getLogger(__name__)

def _connect():
    host   = os.getenv("SPLUNK_HOST", "localhost")
    port   = int(os.getenv("SPLUNK_PORT", "8090"))
    scheme = os.getenv("SPLUNK_SCHEME", "https")
    verify = os.getenv("SPLUNK_VERIFY", "false").lower() == "true"
    token  = os.getenv("SPLUNK_TOKEN")
    user   = os.getenv("SPLUNK_USERNAME")
    pwd    = os.getenv("SPLUNK_PASSWORD")

    kwargs = dict(host=host, port=port, scheme=scheme, verify=verify, autologin=True)
    if token:
        kwargs["splunkToken"] = token
    elif user and pwd:
        kwargs.update(username=user, password=pwd)
    else:
        raise RuntimeError("Set SPLUNK_TOKEN or SPLUNK_USERNAME/SPLUNK_PASSWORD")
    return client.connect(**kwargs)

@mcp.tool
def list_indexes() -> List[str]:
    """List Splunk index names."""
    svc = _connect()
    return [i.name for i in svc.indexes]



# @mcp.tool
# def search(query: str, earliest: str = "-5d", latest: str = "now", count: int = 100) -> List[Dict]:
#     """Run a Splunk search and return rows."""
#     svc = _connect()
#     stream = svc.jobs.oneshot(
#         f"search {query}", earliest_time=earliest, latest_time=latest, output_mode="json", count=count
#     )
#     rr = results.ResultsReader(stream)
#     return [dict(r) for r in rr if isinstance(r, dict)]

@mcp.tool()
async def search_splunk(search_query: str, earliest_time: str = "-24h", latest_time: str = "now", max_results: int = 100) -> List[Dict[str, Any]]:
    """
    Execute a Splunk search query and return the results.

    Args:
        search_query: The search query to execute
        earliest_time: Start time for the search (default: 24 hours ago)
        latest_time: End time for the search (default: now)
        max_results: Maximum number of results to return (default: 100)

    Returns:
        List of search results
    """
    if not search_query:
        raise ValueError("Search query cannot be empty")

    # Prepend 'search' if not starting with '|' or 'search' (case-insensitive)
    stripped_query = search_query.lstrip()
    if not (stripped_query.startswith('|') or stripped_query.lower().startswith('search')):
        search_query = f"search {search_query}"

    try:
        svc = _connect()
        logger.info(f"🔍 Executing search: {search_query}")

        # Create the search job
        kwargs_search = {
            "earliest_time": earliest_time,
            "latest_time": latest_time,
            "preview": False,
            "exec_mode": "blocking"
        }

        job = svc.jobs.create(search_query, **kwargs_search)

        # Get the results
     #   result_stream = job.results(output_mode='json', count=max_results)
     #   results_data = json.loads(result_stream.read().decode('utf-8'))

        # Fetch results as JSON and extract only _raw
        result_stream = job.results(output_mode="json", count=max_results)
        payload = json.loads(result_stream.read().decode("utf-8"))
        rows = payload.get("results", [])

        # Return only raws as messages
        messages_only = [{"message": r["_raw"]} for r in rows if "_raw" in r]
        logger.info(f"✅ Returned {len(messages_only)} raw messages")
        return messages_only

       # return results_data.get("results", [])

    except Exception as e:
        logger.error(f"❌ Search failed: {str(e)}")
        raise

@mcp.tool
def search(query: str,
           earliest: str = "-7d",
           latest: str = "now",
           count: int = 200) -> List[Dict]:
    """
    Run a Splunk search and return rows. Accepts plain terms ('index=...') or pipelines ('| tstats ...').
    """
    if not query or not query.strip():
        raise ValueError("query is empty")
    q = query.strip()
    if not (q.startswith("search ") or q.startswith("|")):
        q = "search " + q

    svc = _connect()
    try:
        stream = svc.jobs.oneshot(q,
                                  earliest_time=earliest,
                                  latest_time=latest,
                                  output_mode="json",
                                  count=count)
    except HTTPError as e:
        return [{"error": "splunk_http_error",
                 "status": getattr(e, "status", None),
                 "message": str(e),
                 "query": q}]

    rr = results.ResultsReader(stream)
    rows = [dict(r) for r in rr if isinstance(r, dict)]
    msgs = getattr(rr, "messages", None)
    if not rows and msgs:
        return [{"warning": "no_rows", "messages": [str(m) for m in msgs],
                 "query": q, "earliest": earliest, "latest": latest}]
    return rows

@mcp.tool
def search_index(
        index: str,
        filter: str = "",
        earliest: str = "-5d",
        latest: str = "now",
        fields: Optional[List[str]] = None,
        limit: int = 100
) -> List[Dict]:
    """
    Query a Splunk index and return up to `limit` rows as JSON.
    - `filter` can be additional terms (e.g., `app=MonthlyPaymentsManagement level=ERROR`)
      OR a pipeline starting with `|` (e.g., `| stats count by sourcetype`).
    - Set `fields` to limit returned fields.
    """
    if not index:
        raise ValueError("index is required")

    base = f"search index={index}"
    filt = (filter or "").strip()

    if filt:
        if filt.startswith("|"):           # pipeline
            q = f"{base} {filt}"
        elif filt.startswith("search "):   # redundant 'search' — merge
            q = f"{base} {filt[len('search '):]}"
        else:
            q = f"{base} {filt}"           # plain terms
    else:
        q = base

    if fields:
        q += " | fields " + " ".join(fields)

    # Add a deterministic order if no transform present
    if "| sort" not in q and "| stats" not in q and "| tstats" not in q:
        q += " | sort - _time"

    svc = _connect()
    try:
        stream = svc.jobs.oneshot(
            q,
            earliest_time=earliest,
            latest_time=latest,
            output_mode="json",
            count=limit
        )
    except HTTPError as e:
        return [{"error": "splunk_http_error", "status": getattr(e, "status", None), "message": str(e), "query": q}]

    rr = results.ResultsReader(stream)
    rows = [dict(r) for r in rr if isinstance(r, dict)]
    # If Splunk returned only messages (warnings), surface them nicely
    msgs = getattr(rr, "messages", [])
    if not rows and msgs:
        return [{"warning": "no_rows", "messages": [str(m) for m in msgs], "query": q, "earliest": earliest, "latest": latest}]
    return rows

@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

if __name__ == "__main__":
#    mcp.run(transport="http", host="127.0.0.1", port=8000)
    mcp.run()

