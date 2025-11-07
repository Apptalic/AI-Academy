import streamlit as st
from utils import process_file, process_url
from agent import create_agent, get_mini_course

agent = create_agent()

st.title("Mini-Course Generator Agent")

st.sidebar.header("Input Options")
input_option = st.sidebar.radio("Choose Input Type:", ("Upload a file", "Enter a document URL"))

if input_option == "Upload a file":
  uploaded_file = st.file_uploader("Upload a PDF or TXT file", type=["pdf", "txt"])
  if uploaded_file:

    # Creating a session date do when i hit download button it doesn't reprocess
    file_key = f"mini_course_{uploaded_file.name}"
    if file_key not in st.session_state:

      with st.spinner("Processing file..."):
        try: 
          st.info("Extracting content from the uploaded file...")
          content = process_file(uploaded_file)


          st.info("Generating the final mini-course...")
          mini_course = get_mini_course(content)

          st.session_state[file_key] = mini_course
        except Exception as e:
          st.error(f"Error processing file: {str(e)}") 
          st.session_state[file_key] = ""

    mini_course = st.session_state.get(file_key, "")
    if mini_course:
      st.success("Mini courses created!")
      st.text_area("Generated mini-course", mini_course, height=400)
      st.download_button(
        label="Download Mini-Course",
        data=mini_course,
        file_name="mini_course.md",
        mime="text/markdown",
      )


elif input_option == "Enter a document URL":
  st.info("Please enter the URL of your blog post. Note: Google Docs or Notion links are not supported, you may need to download it and upload it to use it.")
  url = st.text_input("Enter the URL of your blog post")
  if url: 

    # Use URL as file key
    url_key = f"mini_course_{url}"

    # Validate if the url is a google docs link
    if "doc.google.com" in url: 
      st.error("Google docs are not supported. Enter a blog post URL.")
    elif "www.notion.so" in url:
      st.error('Notion links are not supported. Enter a blog post URL.')
    else: 
      if url_key not in st.session_state:
        with st.spinner("Fetching and processing content..."):
          try:
            st.info("Extracting content from the URL...")
            content = process_url(url)


            st.info("Generating the final mini-course...")
            mini_course = get_mini_course(content)
            st.session_state[url_key] = mini_course
          except Exception as e:
            st.error(f"Error processing URL: {str(e)}")
            st.session_state[url_key] = ""
      
      mini_course =st.session_state.get(url_key, "")
      if mini_course:
        st.success("Mini courses created!")
        st.text_area("Generated Mini-course", mini_course, height=400)
        st.download_button(
          label="Download Mini-course",
          data=mini_course,
          file_name="mini_course.md",
          mime="text/markdown",
        )
