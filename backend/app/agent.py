import matplotlib
matplotlib.use("Agg")

import os
import io
import base64
import matplotlib.pyplot as plt
import pandas as pd

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

from backend.app.data_loader import get_dataframe

# Load environment
load_dotenv()

# Load dataframe
df = get_dataframe()

# Initialize OpenAI model
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)

# TOOL 1: Data Analysis
@tool
def analyze_data(query: str) -> str:
    """
    Use this tool for answering analytical questions about the Titanic dataset.
    Accepts ONLY valid pandas Python code.
    """
    try:
        local_vars = {"df": df, "pd": pd}
        result = eval(query, {}, local_vars)
        return str(result)
    except Exception as e:
        return f"Error in analysis: {str(e)}"


# TOOL 2: Visualization
@tool
def visualize_data(query: str) -> str:
    """
    Executes valid matplotlib Python code using dataframe df.
    The code must generate a plot.
    """
    try:
        local_vars = {"df": df, "plt": plt}

        plt.clf()
        exec(query, {}, local_vars)

        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)

        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()

        global LAST_IMAGE
        LAST_IMAGE = image_base64

        return "Plot generated successfully."

    except Exception as e:
        return f"Error in visualization: {str(e)}"


# Register tools
tools = [analyze_data, visualize_data]

# Prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        ("system",
         """
        You are a data analyst working with a pandas dataframe named df.

        CRITICAL RULES:
        - When using analyze_data tool, you MUST pass ONLY valid pandas Python code.
        - NEVER pass natural language into the tool.
        - The input to analyze_data must be a valid Python expression.
        - Example:
            df['Sex'].value_counts(normalize=True).get('male', 0) * 100

        When using visualize_data tool, you MUST pass ONLY matplotlib Python code.:
        - ALWAYS include:
            - plt.title()
            - plt.xlabel()
            - plt.ylabel()
        - DO NOT use plt.show()
        - DO NOT import matplotlib
        - DO NOT explain anything.
        - DO NOT include text.
        - DO NOT include markdown.
        - DO NOT use plt.show()
        - ONLY raw Python code.
        - Generate complete matplotlib plotting code.
        """
        ),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ]
)

# Create agent
agent = create_tool_calling_agent(llm, tools, prompt)

# Executor
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    return_intermediate_steps=True
)

#Run Agent
def run_agent(question: str):
    global LAST_IMAGE
    LAST_IMAGE = None

    response = agent_executor.invoke({"input": question})

    # Check if visualization tool ran
    if LAST_IMAGE is not None:
        return {
            "answer": "Here is the requested visualization:",
            "image": LAST_IMAGE
        }

    # Otherwise normal text output
    return {
        "answer": response.get("output", ""),
        "image": None
    }