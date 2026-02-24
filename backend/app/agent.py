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

# -------------------------
# TOOL 1: Data Analysis
# -------------------------
@tool
def analyze_data(query: str) -> str:
    """
    Use this tool for answering analytical questions about the Titanic dataset.
    """
    try:
        local_vars = {"df": df, "pd": pd}
        result = eval(query, {}, local_vars)
        return str(result)
    except Exception as e:
        return f"Error in analysis: {str(e)}"


# -------------------------
# TOOL 2: Visualization
# -------------------------
@tool
def visualize_data(query: str) -> str:
    """
    Creates plot from dataframe df.
    Returns special marker instead of raw base64.
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

        # ⚠️ IMPORTANT: store image globally
        global LAST_IMAGE
        LAST_IMAGE = image_base64

        # Return short marker instead of base64
        return "__PLOT_GENERATED__"

    except Exception as e:
        return f"Error in visualization: {str(e)}"


# Register tools
tools = [analyze_data, visualize_data]

# Prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        ("system",
         "You are a data analyst working with a pandas dataframe named df. "
         "For calculations use analyze_data tool and generate only valid pandas code. "
         "For plots use visualize_data tool and generate only matplotlib code. "
         "IMPORTANT RULES: "
         "- Use ONLY the dataframe named df "
         "- DO NOT import libraries "
         "- DO NOT load datasets "
         "- DO NOT use seaborn "
         "- Generate only Python code, nothing else."
        ),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ]
)

# Create agent
agent = create_tool_calling_agent(llm, tools, prompt)

# Executor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


def run_agent(question: str):
    response = agent_executor.invoke({"input": question})
    output = response["output"]

    # Detect base64 image (very long string)
    if isinstance(output, str) and len(output) > 1000:
        return {
            "answer": "Here is the requested visualization:",
            "image": output
        }

    return {
        "answer": output,
        "image": None
    }