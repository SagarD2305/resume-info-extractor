import streamlit as st
import PyPDF2
import re
from io import BytesIO

def extract_name(text):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if not lines:
        return ""
    
    # First try to find a line that starts with 'Name:'
    for line in lines[:5]:  # Check first 5 lines
        if re.match(r'^[Nn]ame\s*:', line):
            return re.sub(r'^[Nn]ame\s*:\s*', '', line).strip()
    
    # If no explicit name line found, return first non-empty line
    return lines[0]

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_phone(text):
    # Common phone patterns
    phone_patterns = [
        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # 1234567890, 123-456-7890
        r'\(\d{3}\)[-.]?\d{3}[-.]?\d{4}',   # (123)456-7890
        r'\+\d{1,2}[-.]?\d{3}[-.]?\d{3}[-.]?\d{4}'  # +1-123-456-7890
    ]
    
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # First try to find a line that starts with 'Phone:'
    for line in lines[:10]:
        if re.match(r'^[Pp]hone\s*:', line):
            phone_line = re.sub(r'^[Pp]hone\s*:\s*', '', line)
            # Try each pattern
            for pattern in phone_patterns:
                match = re.search(pattern, phone_line)
                if match:
                    return match.group(0)
    
    # Fallback: look for phone pattern in first few lines
    for line in lines[:10]:
        for pattern in phone_patterns:
            match = re.search(pattern, line)
            if match:
                return match.group(0)
    
    return ""
    
    return ""

def extract_phone(text):
    # More comprehensive phone patterns
    phone_patterns = [
        r'(?:\+\d{1,3}[-.]?)?\s*\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}',  # Standard format
        r'\d{10}',  # Just 10 digits
        r'\d{3}[-.]\d{3}[-.]\d{4}'  # Common separator format
    ]
    
    for pattern in phone_patterns:
        phones = re.findall(pattern, text)
        if phones:
            return phones[0]
    return ""

def extract_email(text):
    # Get all non-empty lines
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # First try to find a line that starts with 'Email:'
    for line in lines[:10]:  # Check first 10 lines
        if re.match(r'^[Ee]mail\s*:', line):
            email_line = re.sub(r'^[Ee]mail\s*:\s*', '', line)
            email_line = email_line.lower().strip()
            if '@' in email_line:
                return email_line
    
    # Fallback: look for email pattern in first few lines
    email_pattern = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
    for line in lines[:10]:
        match = re.search(email_pattern, line.lower())
        if match:
            return match.group(0)
    
    return ""

def extract_skills(text, common_skills):
    found_skills = set()
    text_lower = text.lower()
    
    # Find skills section
    skills_section = ""
    sections = text_lower.split('\n\n')
    for skill in common_skills:
        # Create a pattern that matches the skill as a whole word
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.add(skill)
    
    return sorted(list(found_skills))

def extract_work_experience(text):
    experience_sections = []
    lines = text.split('\n')
    
    # Keywords that might indicate the start of work experience section
    experience_headers = [
        'work experience',
        'professional experience',
        'employment history',
        'work history'
    ]
    
    # Keywords that might indicate the start of a new section
    other_sections = [
        'education',
        'skills',
        'certifications',
        'awards',
        'projects',
        'languages',
        'interests',
        'references'
    ]
    
    in_experience_section = False
    current_section = []
    
    for line in lines:
        line = line.strip()
        if not line:  # Skip empty lines
            continue
        
        line_lower = line.lower()
        
        # Check if we've found the start of work experience section
        if any(header in line_lower for header in experience_headers):
            in_experience_section = True
            continue
        
        # Check if we've reached a different section
        if any(section in line_lower for section in other_sections):
            if in_experience_section and current_section:
                experience_sections.append('\n'.join(current_section))
                current_section = []
            in_experience_section = False
            continue
        
        # If we're in the experience section, add the line
        if in_experience_section:
            current_section.append(line)
    
    # Add the last section if we were still in experience
    if in_experience_section and current_section:
        experience_sections.append('\n'.join(current_section))
    
    return experience_sections

def main():
    try:
        st.set_page_config(
            page_title="Resume Information Extractor",
            page_icon="📄",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    except Exception as e:
        st.write(f"Note: {str(e)}")
    
    # Set up the main page
    st.title("📄 Resume Information Extractor")
    st.write("Upload a resume PDF to extract key information")
    
    # Comprehensive skills list
    common_skills = [
        # Programming Languages
        "Python", "Java", "JavaScript", "C++", "C#", "Ruby", "PHP", "Swift", "Kotlin", "Go", "Rust",
        "TypeScript", "SQL", "R", "MATLAB", "Scala", "Perl", "Shell", "Bash",
        
        # Web Technologies
        "HTML", "CSS", "React", "Angular", "Vue.js", "Node.js", "Django", "Flask", "Spring",
        "ASP.NET", "Express.js", "jQuery", "Bootstrap", "Sass", "REST API", "GraphQL",
        
        # Databases
        "MySQL", "PostgreSQL", "MongoDB", "Oracle", "SQL Server", "Redis", "Elasticsearch",
        
        # Cloud & DevOps
        "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Jenkins", "Git", "CI/CD",
        "Terraform", "Ansible", "Linux", "DevOps", "Microservices",
        
        # Data Science & AI
        "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Scikit-learn",
        "Data Analysis", "Data Science", "Natural Language Processing", "Computer Vision",
        "Statistical Analysis", "Big Data", "Hadoop", "Spark",
        
        # Soft Skills
        "Project Management", "Team Leadership", "Communication", "Problem Solving",
        "Critical Thinking", "Agile", "Scrum", "Time Management", "Collaboration",
        "Presentation Skills", "Strategic Planning", "Analytical Skills"
    ]
    
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        with st.spinner('Extracting information from resume...'):
            # Read PDF content
            pdf_bytes = BytesIO(uploaded_file.read())
            text = extract_text_from_pdf(pdf_bytes)
            
            # Extract information
            name = extract_name(text)
            email = extract_email(text)
            phone = extract_phone(text)
            skills = extract_skills(text, common_skills)
            experience = extract_work_experience(text)
            
            # Debug information in expanded section
            with st.expander("Debug Information"):
                st.write("First 5 lines of resume:")
                first_lines = [line.strip() for line in text.split('\n') if line.strip()][:5]
                for i, line in enumerate(first_lines, 1):
                    st.text(f"Line {i}: {line}")
                
                # Show exact content of line 2 with special characters
                if len(first_lines) >= 2:
                    st.write("\nDetailed analysis of line 2 (email line):")
                    email_line = first_lines[1]
                    st.text(f"Raw content: {repr(email_line)}")
                    st.text(f"Length: {len(email_line)}")
                    st.text(f"Characters (decimal): {[ord(c) for c in email_line]}")
            
            # Display results in a clean layout
            st.subheader("📋 Extracted Information")
            
            # Personal Information Section
            personal_info_container = st.container()
            with personal_info_container:
                st.markdown("### 👤 Personal Information")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Name:** {name if name else 'Not found'}")
                with col2:
                    st.markdown(f"**Email:** {email if email else 'Not found'}")
                with col3:
                    st.markdown(f"**Phone:** {phone if phone else 'Not found'}")
            
            # Skills Section
            skills_container = st.container()
            with skills_container:
                st.markdown("### 🛠️ Skills")
                if skills:
                    # Create a more visual representation of skills
                    skills_html = ' • '.join([f'<span style="background-color: #f0f2f6; padding: 2px 6px; margin: 2px; border-radius: 3px;">{skill}</span>' for skill in skills])
                    st.markdown(skills_html, unsafe_allow_html=True)
                else:
                    st.write("No skills found")
            
            # Work Experience Section
            experience_container = st.container()
            with experience_container:
                st.markdown("### 💼 Work Experience")
                if experience:
                    for i, exp in enumerate(experience, 1):
                        with st.expander(f"Experience {i}"):
                            st.write(exp)
                else:
                    st.write("No work experience found")
            
            # Add download button for extracted information
            experience_text = '\n\n'.join(experience)
            skills_text = ', '.join(skills)
            extracted_info = f"""Resume Information Summary

Personal Information:
- Name: {name}
- Email: {email}
- Phone: {phone}

Skills:
{skills_text}

Work Experience:
{experience_text}"""
            
            st.download_button(
                label="Download Extracted Information",
                data=extracted_info,
                file_name="resume_summary.txt",
                mime="text/plain"
            )

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.error("If this error persists, please refresh the page or contact support.")
