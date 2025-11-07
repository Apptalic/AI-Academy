from crewai import Agent, Task, LLM, Crew, Process
from crewai_tools import TavilySearchTool
from dotenv import load_dotenv
from utils import generate_podcast_audio
import os

load_dotenv()

llm = LLM(
  model="openai/gpt-4o",
  temperature=0.8,
  api_key=os.getenv("OPENAI_API_KEY")
)

web_search_tool = TavilySearchTool(api_key=os.getenv("TAVILY_API_KEY"))

researcher_agent = Agent(
  name="Researcher Agent",
  role="Podcast Researcher",
  goal="Research the given topic using both web search and LLM knowledge, and summarize key points.",
  backstory="""
  You are an expert at researching topics for podcast channels and understanding audience preferences, perfomance metrics and recent trends.
  This is important for understanding the topics, and most asked questions related to the topic which would attract a wide audience. 
  You are good at coming up with a research summary that would help the script writer write better. 
  """,
  tools=[web_search_tool],
  prompt_template=(
        "Research the topic: {topic}. "  
        "Use both your own knowledge and the latest information from web search. "
        "Focus specifically on: \n"
        "1. Recent developments and updates about this topic\n"
        "2. Impact and significance of these changes\n"
        "3. Community reactions and discussions\n"
        "Summarize the most important and interesting points in a concise, clear format."
    ),
  llm=llm
)

writer_agent = Agent(
  name="Writer Agent",
  role="Podcast Script writer",
  goal="Write a detailed podcast script based on the research summary and it must follow the standard podcast script structure.",
  backstory="""
  You are a professional script writer for podcast channels. 
  You understand recent trends and your writing follows the standard podcast script structure that fits a podcast target audience. 
  You are good at structuring scripts in a way that is easy to follow and understand, while also being entertaining
  """,
  prompt_template=(
    "Using the research summary, write a well detailed, lengthy podcast script that follows the standard structure."
    "Ensure the script is entertaining, has a great flow for anyone to understand, and answers most asked questions based on the research summary."
    "The script should not go outside of the research summary to avoid confusion, it can have funny or famous quotes based on the scene/tone"
  ),
  llm=llm 
)

editor_agent = Agent(
  name="Editor Agent",
  role="Podcast Script Editor",
  goal="Edit the podcast script by following SEO practices and improving the tone and clarity",
  backstory="""
  You are an expert at editing a podcast script to following SEO standards and improve the tone, flow and clarity. 
  This is important to avoid having a poor flow that makes listener feel confused or bored. 
  It is important that the script is entertaining while passing the message across. You are good at following these principles to edit the podcast script. 
  """,
  prompt_template=(
    "Edit the podcast script to follow the following rules:"
    "1. Should be well understood by the target audience"
    "2. Have a great flow and a friendly tone"
    "3. Should be entertaining to appeal the target audience"
    "The edits should focus on improving the podcast script"
  ),
  llm=llm
)


# Tasks for Agents
researcher_task = Task(
  name="research_task",
  description="""
    Research the given podcast topic '{topic}' using both web search and your own knowledge.
    Focus on finding recent, accurate information about the topic.
    Your research should include:
    - Latest developments and updates
    - Expert opinions and community reactions
    - Technical details and practical implications
    Summarize the findings in a clear, structured format.
  """,
  expected_output="""
    A well-structured research summary (3-6 paragraphs) covering:
    - Key facts and background about the topic
    - Recent trends or news (if available)
    - Most asked questions or audience interests
    - Any relevant statistics or notable quotes
    The summary should be clear, concise and ready for use by a podcast script writer.
  """,
  agent=researcher_agent,
  input=lambda inputs: {"topic": inputs["topic"]},
  tools=[web_search_tool]
)

writer_task = Task(
  name="writer_task",
  description="""
  Write a podcast script based on the research summary and it should follow the standard podcast script structure. 
  Ensure the script has a great flow, clear and doesn't go off topic. 
  """,
  expected_output="""
  A well-written and structured podcast script (5-7 paragraphs). 
  The script should be engaging, well-written and have a great flow, it should be divided into secrions. 
  Each section should have a good transition into the next and include jokes or quotes based on the target audience for the podcast.
  """,
  agent=writer_agent,
  input=lambda results: {"research_summary": results["research_task"]}
)

editor_task = Task(
  name="editor_task",
  description="Review and edit the podcast  to follow SEO practices, improving the tone and clarity",
  expected_output="""
  A throughly edited podcast script that follows these rules:
  1. Should be well understood by the target audience
  2. Have a great flow and a friendly tone
  3. Should be entertaining to appeal the target audience
  The edited podcast script should be well polished to be a better script. 
  """,
  agent=editor_agent,
  input=lambda results: {"script": results["writer_task"]}
)

# Agent orchestration
crew = Crew(
  agents=[researcher_agent, writer_agent, editor_agent],
  tasks=[researcher_task, writer_task, editor_task],
  process=Process.sequential,
  verbose=True
)


# def main():
#     topic = input("Enter your podcast topic: ")
#     print(f"Debug - Input topic: {topic}")
    
#     # Run the Crew workflow
#     results = crew.kickoff(inputs={"topic": topic})
#     print("\n--- Edited Podcast Script ---\n")
#     print(results)  
#     print("\n----------------------------\n")

#     # Display the final script text
#     final_script = results.raw  

#     # Ask for user approval
#     approval = input("Do you approve this script for audio generation? (y/n): ").strip().lower()
#     if approval != "y":
#         print("You chose not to proceed. You can edit the script manually and rerun the audio generation.")
#         return

#     # Generate podcast audio
#     print("Generating podcast audio...")
#     audio_bytes = generate_podcast_audio(final_script) 

#     # Save the audio file
#     audio_filename = "podcast_audio.mp3"
#     with open(audio_filename, "wb") as f:
#         f.write(audio_bytes)
#     print(f"Audio generated and saved as {audio_filename}")

# if __name__ == "__main__":
#     main()