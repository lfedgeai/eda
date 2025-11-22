#!/usr/bin/env python3
import sys
from mcp.server.fastmcp import FastMCP
from run_edge_data_agent import run_edge_data_agent  # ensure run_rag_all is importable from here

mcp = FastMCP("Edge Data Agent")

@mcp.tool()
def run_rag_mcp(query: str) -> str:
    """
    Runs the aggregated RAG process for all data directories in the registry.
    """
    return run_edge_data_agent(query)

if __name__ == "__main__":
    # Run the server; this is blocking
    mcp.run(transport="stdio")
