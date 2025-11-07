import streamlit as st 
from agent import crew
from utils import generate_podcast_audio, create_zip


# State variables to store data in session data
if "final_script" not in st.session_state:
  st.session_state.final_script = None

if "script_rejected" not in st.session_state:
  st.session_state.script_rejected = False

if "audio_generated" not in st.session_state:
    st.session_state.audio_generated = False

if "audio_bytes" not in st.session_state:
    st.session_state.audio_bytes = None

# Reject script callback
def reject_script():
  st.session_state.script_rejected = True


st.title("Podcast Generator Agent")
st.write("Built with Spitch TTS and CrewAI")
st.write("Create scripts, approve scripts, and generate a podcast episode in a single click.")

topic = st.text_input("Enter a Topic:")
if st.button("Start the Agent!"): 
  if not topic: 
    st.error("Enter a topic to start the agent.")
  else: 
    st.session_state.audio_generated = False 
    st.session_state.script_rejected = False
    st.session_state.final_script = None
    st.session_state.audio_bytes = None
    try: 
      with st.spinner("Running agents..."):
        # Run the crew agents workflow
        results = crew.kickoff(inputs={"topic": topic})
        st.session_state.final_script = results.raw

        # Display the script for human-in-the-loop approval
        st.subheader("Generated Podcast Script")
        st.text_area("Your final script", value=st.session_state.final_script, height=300)
    except Exception as e:
      st.error(f"An error occured while running the agents: {e}")

# Human approval 
if (
    st.session_state.final_script 
    and not st.session_state.script_rejected 
    and not st.session_state.audio_generated
): 
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Approve Script"):
            try: 
                with st.spinner("Generating podcast audio..."):
                    audio_bytes = generate_podcast_audio(st.session_state.final_script)
                    st.session_state.audio_generated = True
                    st.session_state.audio_bytes = audio_bytes
            except Exception as e:
                st.error(f"Error generating podcast audio: {e}")
    with col2:
        st.button("Reject Script", on_click=reject_script)

# Show warning if script is rejected
if st.session_state.script_rejected:
    st.warning("You rejected the script. Modify the topic or rerun the agent.")

# Show audio and download only after approval
if st.session_state.audio_generated and st.session_state.audio_bytes:
    st.subheader("Generated Podcast")
    st.audio(st.session_state.audio_bytes, format="audio/mp3")
    st.success("Podcast audio generated.")
    try:
        st.download_button(
            label="Download All (Script + Audio)",
            data=create_zip(st.session_state.final_script, st.session_state.audio_bytes),
            file_name="podcast_episode.zip",
            mime="application/zip"
        )
    except Exception as e:
        st.error(f"Error generating zip file: {e}")