/**
This project demonstrates how to create MCP serer and connect to Claud.ai & Splunk 
*/

Step 1:

Install Python

brew install python3



Installing UV :

curl -LsSf https://astral.sh/uv/install.sh | sh


Step 2 :

Create Project folder in your local. “splunk-fastmcp”



Step 3:

Get a Splunk API token & URL from your enterprise OPS team



Step 4: Run below command in terminal

# install deps (choose ONE of the three)

# a) UV (fast)

pip install uv && uv sync



Step 5:

# API port is different then the one which we use for the Frontend App.

export SPLUNK_HOST="prd-xxxxx.splunkcloud.com"

export SPLUNK_PORT="8089"

export SPLUNK_TOKEN="YOUR_TOKEN"      # preferred over username/password

export VERIFY_SSL="true"



Step 6:

Add attached server.py into your project folder. Please adapt variables.



Step 7:

Run this command, Adapt the URI



/Users/umangparekh/Documents/splunkMCP/splunk-fastmcp/.venv/bin/python3 server.py





This displays if fastMCP is started.




Step 8:

Verify if MCP is up or not using MCP Inspector



npx @modelcontextprotocol/inspector \

/Users/umangparekh/Documents/splunkMCP/splunk-fastmcp/.venv/bin/python3 \

/Users/umangparekh/Documents/splunkMCP/splunk-fastmcp/server.py