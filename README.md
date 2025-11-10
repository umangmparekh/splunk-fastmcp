Splunk FastMCP – POC with Claude.ai

This project is a Proof of Concept (POC) demonstrating how to create an MCP server and connect it to Claude.ai and Splunk.

🧩 Prerequisites

macOS or Linux environment

Python 3
installed

Access to your enterprise Splunk instance (with API token & URL)

⚙️ Step 1: 
Install Python
brew install python3

⚡ Step 2: 

Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

📁 Step 3: 
Create a Project Folder
Create a local folder for your project:

mkdir splunk-fastmcp
cd splunk-fastmcp

🔐 Step 4: 

Get Splunk Credentials
Obtain your Splunk API Token and Splunk URL from your Enterprise OPS Team.

📦 Step 5: 

Install Dependencies
Choose one of the following methods to install dependencies:

Option A: 
Using UV (recommended)
pip install uv && uv sync

🌍 Step 6: 

Set Environment Variables
Set up the Splunk configuration in your terminal:

export SPLUNK_HOST="prd-xxxxx.splunkcloud.com"
export SPLUNK_PORT="8089"
export SPLUNK_TOKEN="YOUR_TOKEN"      # preferred over username/password
export VERIFY_SSL="true"

🧠 Step 7: 

Add and Run the Server
Add the provided server.py file into your project folder.
Adapt the variable values as needed, then run the following command (adjust the path as per your setup):

/Users/umangparekh/Documents/splunkMCP/splunk-fastmcp/.venv/bin/python3 server.py

If successful, you’ll see a confirmation message that FastMCP has started.

🧩 Step 8: 

Verify the MCP Server
Use the MCP Inspector to check if your MCP server is running correctly:

npx @modelcontextprotocol/inspector \
/Users/umangparekh/Documents/splunkMCP/splunk-fastmcp/.venv/bin/python3 \
/Users/umangparekh/Documents/splunkMCP/splunk-fastmcp/server.py

✅ Summary

After completing these steps, your MCP Server should be successfully connected to Claude.ai and Splunk, 
enabling you to query and interact with your enterprise data securely.