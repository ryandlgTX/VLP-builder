import os
import logging
from typing import Optional, List

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import streamlit as st
from dotenv import load_dotenv
import anthropic

# Load environment variables
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")

def get_reference_files(grade: str) -> List[str]:
    """
    Maps the selected grade level to a list of reference PDF file names.
    Note: For Algebra 1, Algebra 2, and Geometry, we map to high school (HS) materials.
    """
    if grade in ["Kindergarten", "Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5"]:
        return [
            "K-5 CC & OA Progressions.pdf",
            "K-5 NBT Progressions.pdf",
            "K-5 MD (Data) Progression.pdf",
            "K-5 MD (Measurement) Progression.pdf",
            "K-6 Geometry Progression.pdf",
            "3-5 Progression on Operations—Fractions.pdf",
            "3-5 NBT Progressions.pdf"
        ]
    elif grade in ["Grade 6", "Grade 7", "Grade 8"]:
        return [
            "6-7 RP Progression.pdf",
            "6-8 EE Progression.pdf",
            "6-8 SP Progression.pdf",
            "6-8 NS & HS N-RN Progression.pdf",
            "Geometry Progression Doc 7-12.pdf",
            "7-HS Geometry Progression.pdf"
        ]
    elif grade in ["Algebra 1", "Algebra 2", "Geometry"]:
        return [
            "6-8 NS & HS N-RN Progression.pdf",
            "8-HS Functions Progression.pdf",
            "HS Algebra Progression.pdf",
            "HS.S Progression.pdf",
            "HS.N-Q - Quantity Progression.pdf",
            "HS Modeling Progression.pdf",
            "Geometry Progression Doc 7-12.pdf",
            "7-HS Geometry Progression.pdf"
        ]
    else:
        return []

def get_response(grade: str,
                 curr_section_id: str,
                 curr_section_overview: str,
                 parent_section_ids: list,
                 parent_section_overviews: list,
                 grandparent_section_ids: list,
                 grandparent_section_overviews: list) -> str:
    """Generate vertical learning progression content using the AI model."""
    client = anthropic.Anthropic(api_key=api_key)
    
    # Prepare Parent Sections strings (join non-empty values)
    parent_ids_str = "\n".join([pid for pid in parent_section_ids if pid])
    parent_overviews_str = "\n".join([pov for pov in parent_section_overviews if pov])
    
    # Prepare Grandparent Sections strings (join non-empty values)
    grandparent_ids_str = "\n".join([gid for gid in grandparent_section_ids if gid])
    grandparent_overviews_str = "\n".join([gov for gov in grandparent_section_overviews if gov])
    
    # Get reference file names based on the selected grade
    ref_files = get_reference_files(grade)
    ref_files_str = "\n".join(ref_files)
    
    prompt = f"""
# CONTEXT #
I am a math curriculum writer creating content for teachers to help them better understand the content being addressed in a current section of the curriculum. I want to give them background information on what their students have learned before the current section to help make connections and support their students.

# INPUTS #
- Grade Level:
{grade}
- Current Section:
{curr_section_id}
- Current Section Overview:
{curr_section_overview}
- Parent Sections:
{parent_ids_str}
- Parent Section Overview:
{parent_overviews_str}
- Grandparent Sections:
{grandparent_ids_str}
- Grandparent Section Overview:
{grandparent_overviews_str}

# REFERENCE MATERIALS #
The following reference PDFs are selected based on the grade level:
{ref_files_str}

# STEPS #

>>>Step1 - Build your knowledge base
a. Review the section overviews provided.
b. Review the attached progression documents to find connections to these overviews and gain a better understanding of how these ideas develop across grade levels.
c. Write a summary of your findings citing information from the progression documents as appropriate.

>>>Step2 - Generate a vertical list of skills
a. Using the summary generated in {{Step1}}, generate a list of 2-4 skills that students develop in each parent section and grandparent section (if provided) that connect to the skills needed to be successful in the current section.
***Focus on skills that have the biggest impact on success in {curr_section_overview}***
b. If a grandparent section is provided, develop a 1-2 sentence summary of the skills listed for the grandparent section explaining how they prepare students for the content in the parent sections. == {{SUMMARY2}}
c. Develop a 1-2 sentence summary of the skills listed for the parent sections explaining how they prepare students for the content in the current section. == {{SUMMARY1}}

>>>Step3 - Misconceptions and skills reference for support
a. Review the progression documents in your knowledge base to understand common misconceptions or mistakes students make when working skills in the current section.
b. Develop a list of 2-4 misconceptions or mistakes students make when working skills in {curr_section_overview}. == {{MISCON}}
c. For each item in {{MISCON}}, explain how teachers could use a skill from the parent or grandparent sections (if provided) to address the misconception. == {{SUPPORT}}
***In your reference include the grade level and section where these skills are practiced***

***NOTE: Only output content in this section that is relevant to the work being done in {curr_section_overview}. Supports in this section should be connected to the content covered in the parent sections and grandparent sections (if provided).***

# STYLE #
I want this to be in the style of a curriculum developer and expert in vertical progressions of learning. You also have experience as an instructional coach and communicate ideas effectively in a way that is approachable and easy to understand. When communicating about mathematical ideas you use only the most relevant mathematical language found in the progression documents attached.

# TONE #
Educational and professional.

# AUDIENCE #
Primarily teachers. Secondarily, administrators and parents/guardians.

# RESPONSE #

Vertical Skills:

{grandparent_ids_str}
- [Skill from {grandparent_overviews_str}]
- [Skill from {grandparent_overviews_str}]
- [Skill from {grandparent_overviews_str}] (If Provided)
- [Skill from {grandparent_overviews_str}] (If Provided)
{{SUMMARY2}}


{parent_ids_str}
- [Skill from {parent_overviews_str}]
- [Skill from {parent_overviews_str}]
- [Skill from {parent_overviews_str}] (If Provided)
- [Skill from {parent_overviews_str}] (If Provided)
{{SUMMARY1}}

{curr_section_id} Misconceptions & Supports
- {{MISCON}} Item 1  
– {{SUPPORT}} Item 1
- {{MISCON}} Item 2  
– {{SUPPORT}} Item 2
- {{MISCON}} Item 3 (If Provided)
– {{SUPPORT}} Item 3 (If Provided)
- {{MISCON}} Item 4 (If Provided)
– {{SUPPORT}} Item 4 (If Provided)
    """
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        system="You are a curriculum developer and expert in vertical progressions of learning.",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=4000,
        stream=False
    )
    
    return response.content[0].text

# Streamlit UI
st.title("Vertical Learning Progression Generator")

# Current Section Inputs
st.header("Current Section")

# Grade Level Selection
grade = st.selectbox("Select Grade Level:", 
                     ["Kindergarten", "Grade 1", "Grade 2", "Grade 3", "Grade 4", 
                      "Grade 5", "Grade 6", "Grade 7", "Grade 8", "Algebra 1", "Algebra 2", "Geometry"])

curr_section_id = st.text_input("Current Section ID:")
curr_section_overview = st.text_area("Current Section Overview:", height=100)

# Parent Sections Inputs
st.header("Parent Sections")
st.markdown("Input the section IDs and Names and Overviews below. You do not need to complete all fields.")
parent_cols = st.columns(3)
parent_section_ids = []
for i in range(3):
    with parent_cols[i]:
        parent_section_ids.append(st.text_input(f"Parent Section ID {i+1}"))

parent_overview_cols = st.columns(3)
parent_section_overviews = []
for i in range(3):
    with parent_overview_cols[i]:
        parent_section_overviews.append(st.text_area(f"Parent Section Overview {i+1}", height=100))

# Grandparent Sections Inputs
st.header("Grandparent Sections")
st.markdown("Input the section IDs and Names and Overviews below. You do not need to complete all fields.")
grandparent_cols = st.columns(3)
grandparent_section_ids = []
for i in range(3):
    with grandparent_cols[i]:
         grandparent_section_ids.append(st.text_input(f"Grandparent Section ID {i+1}"))

grandparent_overview_cols = st.columns(3)
grandparent_section_overviews = []
for i in range(3):
    with grandparent_overview_cols[i]:
         grandparent_section_overviews.append(st.text_area(f"Grandparent Section Overview {i+1}", height=100))

if st.button("Generate Vertical Progression"):
    if curr_section_id and curr_section_overview:
        with st.spinner("Generating vertical progression analysis..."):
            try:
                response_text = get_response(
                    grade,
                    curr_section_id,
                    curr_section_overview,
                    parent_section_ids,
                    parent_section_overviews,
                    grandparent_section_ids,
                    grandparent_section_overviews
                )
                st.success("Vertical progression analysis generated successfully!")
                
                st.markdown(response_text)
                
                with st.expander("Show Raw Text"):
                    st.text_area("Raw Vertical Progression Text", value=response_text, height=400)
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                logger.error(f"Error generating vertical progression analysis: {str(e)}")
    else:
        st.warning("Please fill in the Current Section ID and Overview.")
