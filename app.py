import streamlit as st
import PyPDF2
import spacy
import re
from io import BytesIO

# Load spaCy model
@st.cache_resource
def load_model():
    return spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_email(text):
    # Get all non-empty lines
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Look at line 2 specifically for the email
    if len(lines) >= 2:
        email_line = lines[1]  # 2nd line (0-based index)
        
        # Replace non-breaking spaces with regular spaces
        email_line = email_line.replace('\xa0', ' ')
        
        # If line starts with 'Email :' or similar, remove that prefix
        if 'email' in email_line.lower():
            # Split on ':' and take everything after it
            parts = email_line.split(':', 1)
            if len(parts) > 1:
                email_line = parts[1]
        
        # Clean up the email: remove spaces, convert to lowercase
        email_line = ''.join(email_line.split())  # Remove all whitespace
        email_line = email_line.lower()  # Convert to lowercase
        
        # Simple email pattern
        email_pattern = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
        match = re.search(email_pattern, email_line)
        if match:
            return match.group(0)
    
    # Fallback: try to find any email in the text
    email_pattern = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
    match = re.search(email_pattern, text)
    if match:
        return match.group(0).lower()
    
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

def extract_name(nlp, doc, text):
    # Get all non-empty lines
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Look at line 5 specifically for the name
    if len(lines) >= 5:
        name_line = lines[4]  # 5th line (0-based index)
        # Clean up the name line
        name = name_line.strip()
        # Remove any prefix like 'Name:' if present
        if ':' in name:
            name = name.split(':', 1)[1].strip()
        return name
    
    # Fallback: try spaCy name detection
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    
    return ""

def extract_skills(text, common_skills):
    found_skills = set()
    text_lower = text.lower()
    
    # Find skills section
    skills_section = ""
    sections = text_lower.split('\n\n')
    for i, section in enumerate(sections):
        if any(keyword in section.lower() for keyword in ['skills', 'technical skills', 'core competencies']):
            # Include this section and the next one
            skills_section = '\n'.join(sections[i:i+2])
            break
    
    # If no skills section found, search entire text
    search_text = skills_section if skills_section else text_lower
    
    # Look for skills
    for skill in common_skills:
        skill_lower = skill.lower()
        if skill_lower in search_text:
            found_skills.add(skill)
    
    return sorted(list(found_skills))

def extract_work_experience(text):
    experience_sections = []
    
    # Common section headers
    section_headers = [
        'work experience',
        'professional experience',
        'employment history',
        'work history',
        'experience'
    ]
    
    # Split text into sections
    lines = text.split('\n')
    current_section = []
    in_experience_section = False
    
    for i, line in enumerate(lines):
        line = line.strip()
        line_lower = line.lower()
        
        # Check if this line is a section header
        if any(header in line_lower for header in section_headers):
            in_experience_section = True
            continue
        
        # Check if we've hit the next major section
        if line and len(line) < 50 and line.isupper() and i > 0:
            if in_experience_section:
                if current_section:
                    experience_sections.append('\n'.join(current_section))
                break
        
        if in_experience_section and line:
            current_section.append(line)
    
    # Add the last section if we're still in experience
    if in_experience_section and current_section:
        experience_sections.append('\n'.join(current_section))
    
    return experience_sections

def main():
    st.set_page_config(page_title="Resume Information Extractor", layout="wide")
    st.title("Resume Information Extractor")
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
            
            # Process with spaCy
            nlp = load_model()
            doc = nlp(text)
            
            # Extract information
            name = extract_name(nlp, doc, text)
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
    main()
