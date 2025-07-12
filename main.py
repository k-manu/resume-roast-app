import os
import json
import io
import streamlit as st
import openai
import PyPDF2
from datetime import datetime
from dotenv import load_dotenv
from streamlit_supabase_auth import login_form, logout_button
from supabase import create_client, Client

# ======================
# Configuration Settings
# ======================

# Set page config first
st.set_page_config(
    page_title="Resume Roast - AI Edition", 
    page_icon="🔥",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Load environment variables from .env file
load_dotenv()

# Configure OpenAI API
openai.api_key = os.getenv('OPENAI_API_KEY')

# Load Supabase credentials from Streamlit secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# Initialize Supabase client
@st.cache_resource
def init_supabase() -> Client:
    """Initialize Supabase client"""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# Initialize session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "landing"

if "user_session" not in st.session_state:
    st.session_state.user_session = None

# ======================
# Supabase AI Data Functions
# ======================

def log_processing_event(user_id: str, file_type: str, processing_time: float, roast_length: int, success: bool = True):
    """
    Log AI processing events for analytics (privacy-friendly)
    """
    try:
        result = supabase.table('processing_logs').insert({
            'user_id': user_id,
            'file_type': file_type,
            'processing_time_seconds': processing_time,
            'roast_length_chars': roast_length,
            'success': success,
            'processed_at': datetime.utcnow().isoformat()
        }).execute()
        return result
    except Exception as e:
        st.error(f"Failed to log processing event: {str(e)}")
        return None

def get_user_stats(user_id: str):
    """
    Get user's processing statistics
    """
    try:
        # Try to get stats with the user_id as provided
        result = supabase.table('processing_logs').select('*').eq('user_id', user_id).execute()
        
        if result.data:
            return result.data
        
        # If no data found, the user might not have processed any resumes yet
        return []
        
    except Exception as e:
        # Don't show error to user, just return empty list
        return []

def store_user_preferences(user_id: str, preferences: dict):
    """
    Store user preferences for AI processing
    """
    try:
        # Convert user_id to UUID format if it's a string
        import uuid
        try:
            # Validate UUID format
            uuid_obj = uuid.UUID(user_id)
            user_id_clean = str(uuid_obj)
        except ValueError:
            st.error(f"Invalid user ID format: {user_id}")
            return None
        
        # First, check if record exists
        existing_result = supabase.table('user_preferences').select('*').eq('user_id', user_id_clean).execute()
        
        if existing_result.data:
            # Update existing record
            result = supabase.table('user_preferences').update({
                'preferences': preferences,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('user_id', user_id_clean).execute()
        else:
            # Insert new record
            result = supabase.table('user_preferences').insert({
                'user_id': user_id_clean,
                'preferences': preferences,
                'updated_at': datetime.utcnow().isoformat()
            }).execute()
        
        # Verify the data was actually stored
        verification_result = supabase.table('user_preferences').select('*').eq('user_id', user_id_clean).execute()
        
        if verification_result.data:
            stored_prefs = verification_result.data[0]['preferences']
            # Check if the preferences match what we tried to store
            if stored_prefs == preferences:
                return result
            else:
                return None
        else:
            return None
        
    except Exception as e:
        st.error(f"Failed to store preferences: {str(e)}")
        return None

def get_user_preferences(user_id: str):
    """
    Get user preferences
    """
    try:
        result = supabase.table('user_preferences').select('preferences').eq('user_id', user_id).execute()
        if result.data:
            return result.data[0]['preferences']
        return {}
    except Exception as e:
        return {}

# ======================
# Enhanced AI Processing Function
# ======================

def roast_resume(resume_text: str, user_id: str = None, preferences: dict = None) -> tuple[str, dict]:
    """
    Process resume text through OpenAI for a humorous critique.
    Returns tuple of (roast_result, processing_stats)
    """
    start_time = datetime.now()
    
    # Get user preferences or defaults
    if not preferences:
        preferences = get_user_preferences(user_id) if user_id else {}
    
    roast_style = preferences.get('roast_style', 'balanced')
    humor_level = preferences.get('humor_level', 'medium')
    
    # Customize prompt based on preferences - BRUTAL EDITION
    style_prompts = {
        'gentle': "Tear this resume apart with sharp wit and cutting sarcasm, but don't completely destroy their soul",
        'balanced': "Absolutely demolish this resume like Pete Davidson roasting someone - be merciless, cutting, and brutally honest with zero mercy",
        'savage': "Obliterate this resume with the fury of a thousand suns. Make Gordon Ramsay look like a kindergarten teacher. Show no mercy, no compassion, just pure comedic brutality"
    }
    
    humor_prompts = {
        'low': "Be ruthlessly sarcastic and cutting, but keep it somewhat professional",
        'medium': "Go full savage mode - be cruel, dark, and brutally honest like a comedy roast",
        'high': "Unleash absolute comedic hell - be merciless, savage, and destroy every aspect of this resume with brutal comedy"
    }
    
    # Enhanced brutal prompt
    prompt = f"""{style_prompts.get(roast_style, style_prompts['balanced'])}. 
            {humor_prompts.get(humor_level, humor_prompts['medium'])}. 
            
            You are a savage comedy roast master with the wit of Pete Davidson and the brutal honesty of The Simpsons. 
            Attack every weakness, mock every cliché, and destroy every poorly written section. 
            Be technically brutal about skills, experience, and formatting. 
            Make them question their career choices and life decisions.
            
            Find the most embarrassing and cringe-worthy parts and absolutely demolish them with cutting humor.
            Be merciless about generic phrases, obvious lies, and pathetic attempts at sounding professional.
            
            Keep it under 150 words but make every word count like a surgical strike.
            
            Resume to destroy:
            {resume_text}"""
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a savage comedy roast master who destroys resumes with brutal honesty and cutting humor. You have the wit of Pete Davidson, the ruthlessness of Gordon Ramsay, and the sharp tongue of The Simpsons. Show no mercy. Be technically brutal about every aspect of the resume while maintaining comedic value. Your goal is to make them laugh while simultaneously destroying their confidence."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=350,
            temperature=0.9
        )
        roast_result = response.choices[0].message.content if response.choices else "No response from AI."
        
        # Calculate processing stats
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        processing_stats = {
            'processing_time': processing_time,
            'roast_length': len(roast_result),
            'success': True,
            'model_used': 'gpt-3.5-turbo',
            'roast_style': roast_style,
            'humor_level': humor_level
        }
        
        # Log the event if user is authenticated
        if user_id:
            log_processing_event(
                user_id=user_id,
                file_type='pdf' if resume_text.startswith('%PDF') else 'txt',
                processing_time=processing_time,
                roast_length=len(roast_result),
                success=True
            )
        
        return roast_result, processing_stats
        
    except Exception as e:
        processing_stats = {
            'processing_time': 0,
            'roast_length': 0,
            'success': False,
            'error': str(e)
        }
        
        if user_id:
            log_processing_event(
                user_id=user_id,
                file_type='unknown',
                processing_time=0,
                roast_length=0,
                success=False
            )
        
        return f"Error processing resume: {str(e)}", processing_stats

# ======================
# Page Functions
# ======================

def show_landing_page():
    """
    Quirky landing page with navigation options
    """
    # Header with quirky styling
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='color: #ff6b6b; font-size: 3rem; margin-bottom: 0;'> Resume Roast </h1>
        <h2 style='color: #4ecdc4; font-size: 1.5rem; margin-top: 0;'>AI Edition</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Quirky introduction
    st.markdown("""
    ### Welcome to the digital equivalent of Gordon Ramsay critiquing your career choices! 
    
    **Are you ready to have your resume absolutely *demolished* by AI?** 
    
    Our sophisticated artificial intelligence has been trained on thousands of resumes, countless rejection letters, 
    and probably watched every episode of "The Office" to perfect the art of professional roasting.
    
    ---
    
    **What to expect:**
    - 🔥 Brutally honest feedback that'll make you question your life choices
    - 😂 Dad jokes so bad they're good (just like your resume)
    - 💡 Actually helpful insights buried under layers of sarcasm
    - 🎭 Entertainment value that's worth more than your current salary
    
    ---
    
    **Warning:** ⚠️ 
    *Side effects may include: existential crisis, uncontrollable laughter, sudden urge to rewrite entire resume, 
    and an inexplicable desire to become a professional circus performer instead.*
    
    ---
    """)
    
    # Call-to-action buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Ready to get roasted? ")
        
        if st.button(" Let's Get This Bread (and Roast)", type="primary", use_container_width=True):
            st.session_state.page = "auth"
            st.rerun()
        
        st.markdown("*Don't worry, we won't judge... much 😏*")
    
    # Footer with more quirky text
    st.markdown("""
    ---
    
    <div style='text-align: center; color: #7f8c8d; font-style: italic; padding: 1rem 0;'>
        <p> Made with questionable life choices and excessive caffeine</p>
        <p> "Turning career documents into comedy gold since... well, today!"</p>
    </div>
    """, unsafe_allow_html=True)

def show_auth_page():
    """
    Authentication page with Supabase login/signup
    """
    # Header
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0;'>
        <h1 style='color: #ff6b6b;'>Join the Roast Club</h1>
        <p style='color: #7f8c8d; font-size: 1.1rem;'>Because anonymous roasting just isn't as fun!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Back button
    if st.button("← Back to Landing", type="secondary"):
        st.session_state.page = "landing"
        st.rerun()
    
    st.markdown("---")
    
    # Supabase Authentication
    session = login_form(
        url=SUPABASE_URL,
        apiKey=SUPABASE_KEY
    )
    
    if not session:
        st.info("🎭 Please log in or sign up to access the resume roasting feature.")
        st.warning("📧 If you sign up - check your email for confirmation!")
        
        # Fun waiting messages
        st.markdown("""
        ### While you're here... 🤔
        
        **Fun Fact:** Did you know that the average recruiter spends only 6 seconds looking at your resume? 
        
        Good news! Our AI will spend at least 7 seconds before destroying your hopes and dreams! 
        
        **Pro Tip:** Make sure your email works - we're not sending carrier pigeons! 
        """)
        return
    
    # If authenticated, save session and navigate to main app
    st.session_state.user_session = session
    st.session_state.page = "roast"
    st.rerun()

def show_roast_page():
    """
    Main resume roasting application with AI data processing
    """
    # Check if user is authenticated
    user_session = st.session_state.user_session
    
    if not user_session:
        # Try to get fresh session
        session = login_form(
            url=SUPABASE_URL,
            apiKey=SUPABASE_KEY
        )
        
        if not session:
            st.error("🚫 Access denied! Please go back and authenticate first.")
            if st.button("← Back to Authentication"):
                st.session_state.page = "auth"
                st.rerun()
            return
        st.session_state.user_session = session
        user_session = session
    
    user_id = user_session['user']['id']
    user_email = user_session['user']['email']
    
    # Header
    st.title("🔥 Resume Roast - AI Edition 🔥")
    
    # Sidebar with user info, preferences, and stats
    with st.sidebar:
        st.write(f"🎭 Welcome {user_email}!")
        st.markdown("---")
        
        # User Statistics
        with st.expander("📊 Your Roast Stats", expanded=False):
            user_stats = get_user_stats(user_id)
            if user_stats and len(user_stats) > 0:
                total_roasts = len(user_stats)
                successful_roasts = len([s for s in user_stats if s.get('success', True)])
                avg_processing_time = sum(s.get('processing_time_seconds', 0) for s in user_stats) / len(user_stats)
                
                st.metric("Total Roasts", total_roasts)
                st.metric("Success Rate", f"{(successful_roasts/total_roasts)*100:.1f}%")
                st.metric("Avg Processing Time", f"{avg_processing_time:.2f}s")
                
                # Recent activity
                st.write("🕒 **Recent Activity:**")
                for stat in user_stats[-3:]:  # Last 3 roasts
                    processed_at = stat.get('processed_at', 'Unknown')
                    if processed_at != 'Unknown':
                        try:
                            processed_at = datetime.fromisoformat(processed_at.replace('Z', '+00:00')).strftime('%m/%d %H:%M')
                        except:
                            processed_at = 'Unknown'
                    st.write(f"• {processed_at} - {stat.get('file_type', 'unknown').upper()}")
            else:
                st.info("🎯 **No roasts yet!**")
                st.write("Upload a resume below to get started!")
                st.write("📈 Your roast statistics will appear here after you've processed some resumes.")
        
        # User Preferences
        with st.expander("⚙️ Roast Preferences", expanded=False):
            current_prefs = get_user_preferences(user_id)
            
            roast_style = st.selectbox(
                "Roast Style",
                ["gentle", "balanced", "savage"],
                index=["gentle", "balanced", "savage"].index(current_prefs.get('roast_style', 'balanced')),
                help="Choose how brutal you want the AI to be"
            )
            
            humor_level = st.selectbox(
                "Humor Level", 
                ["low", "medium", "high"],
                index=["low", "medium", "high"].index(current_prefs.get('humor_level', 'medium')),
                help="Control the intensity of jokes and sarcasm"
            )
            
            if st.button("💾 Save Preferences"):
                new_prefs = {
                    'roast_style': roast_style,
                    'humor_level': humor_level
                }
                result = store_user_preferences(user_id, new_prefs)
                if result is not None:
                    st.success("✅ Preferences actually saved and verified!")
                    st.rerun()
                else:
                    st.error("❌ Failed to save preferences. Check debug messages above.")
        
        st.markdown("---")
        if st.button("🏠 Back to Landing"):
            st.session_state.page = "landing"
            st.session_state.user_session = None
            st.rerun()
        logout_button()
    
    st.write("---")
    st.write("Upload your resume and let AI roast it! 🔥")

    uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])

    if uploaded_file:
        resume_text = ""
        file_type = "txt"
        
        if uploaded_file.type == "application/pdf":
            file_type = "pdf"
            try:
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                resume_text = []
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    text = ' '.join(text.split())
                    resume_text.append(text)
                resume_text = '\n\n'.join(resume_text)
            except Exception as e:
                st.error(f"Error reading PDF: {str(e)}")
                return
        else:
            resume_text = uploaded_file.read().decode("utf-8")

        if resume_text:
            # Show file info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info(f"📄 **File:** {uploaded_file.name}")
            with col2:
                st.info(f"📊 **Type:** {file_type.upper()}")
            with col3:
                st.info(f"📝 **Length:** {len(resume_text):,} chars")
            
            if st.button("🌶️ Roast my resume", type="primary"):
                with st.spinner("🔥 Roasting in progress... (This might hurt a little)"):
                    # Get current user preferences
                    user_prefs = get_user_preferences(user_id)
                    
                    # Process the resume
                    roast_result, processing_stats = roast_resume(
                        resume_text, 
                        user_id=user_id,
                        preferences=user_prefs
                    )
                    
                    # Display results
                    st.subheader("🔥 AI's Roast of Your Resume 🔥")
                    st.write(roast_result)
                    
                    # Show processing stats
                    if processing_stats.get('success', False):
                        with st.expander("🤖 Processing Details", expanded=False):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Processing Time", f"{processing_stats['processing_time']:.2f}s")
                            with col2:
                                st.metric("Response Length", f"{processing_stats['roast_length']} chars")
                            with col3:
                                st.metric("Model", processing_stats['model_used'].split('-')[0].title())
                            
                            st.write(f"**Style:** {processing_stats['roast_style'].title()}")
                            st.write(f"**Humor Level:** {processing_stats['humor_level'].title()}")
                    
                    # Fun follow-up messages
                    st.markdown("---")
                    st.success("🎉 Congratulations! You've survived the roast!")
                    st.info("💡 Remember: Every roast is a chance to improve. Or change careers entirely! 😅")
                    
                    # Suggest trying different settings
                    if user_prefs.get('roast_style') == 'gentle':
                        st.warning("💪 Feeling brave? Try the 'savage' roast style for maximum destruction!")
                    elif user_prefs.get('roast_style') == 'savage':
                        st.info("😌 Need a break from the brutality? Try 'gentle' mode for a more supportive critique.")

# ======================
# Main Application
# ======================

def main():
    """
    Main application router
    """
    # Route to appropriate page based on session state
    if st.session_state.page == "landing":
        show_landing_page()
    elif st.session_state.page == "auth":
        show_auth_page()
    elif st.session_state.page == "roast":
        show_roast_page()
    else:
        # Default to landing page
        st.session_state.page = "landing"
        st.rerun()

# ======================
# Entry Point
# ======================

if __name__ == "__main__":
    main()
