import streamlit as st
import json
import time
from datetime import datetime, date
import base64
from io import BytesIO
from PIL import Image
import os

# Import your existing modules
from client import call_ollama_model
from parser import parse_response
from playwright_actions import perform_action

# Page configuration
st.set_page_config(
    page_title="🚗 Car Rental Automation Tool",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .action-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    .success-message {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .error-message {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .info-box {
        background: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .stProgress .st-bo {
        background-color: #667eea;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'automation_history' not in st.session_state:
    st.session_state.automation_history = []
if 'current_action' not in st.session_state:
    st.session_state.current_action = None
if 'screenshots' not in st.session_state:
    st.session_state.screenshots = []

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚗 Car Rental Website Automation Tool</h1>
        <p>Automate your car rental website testing with natural language commands</p>
        <small>Testing: https://automationdemo.vercel.app/</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🎯 Quick Actions")
        
        # Predefined action buttons
        if st.button("🔍 Search for BMW", use_container_width=True):
            execute_automation("search for BMW car")
        
        if st.button("📋 Fill Van Booking Form", use_container_width=True):
            execute_automation("fill booking form for van")
        
        if st.button("💰 Check SUV Pricing", use_container_width=True):
            execute_automation("check SUV pricing")
        
        if st.button("🚙 View Luxury Car Details", use_container_width=True):
            execute_automation("check luxury car details")
        
        if st.button("📞 Test Contact Links", use_container_width=True):
            execute_automation("test contact links")
        
        if st.button("✅ Submit Booking", use_container_width=True):
            execute_automation("submit booking")
        
        if st.button("🔄 Reset Form", use_container_width=True):
            execute_automation("reset form")
        
        st.divider()
        
        # Settings
        st.header("⚙️ Settings")
        st.info("🔧 Browser runs in visible mode for demo purposes")
        take_screenshots = st.checkbox("Take Screenshots", value=True, help="Capture screenshots during automation")
        
        st.divider()
        
        # Available Actions Info
        with st.expander("📖 Available Actions"):
            st.markdown("""
            **Search Actions:**
            - "search for BMW"
            - "find luxury cars"
            
            **Navigation:**
            - "go to cars section"
            - "navigate to pricing"
            - "open booking form"
            
            **Form Actions:**
            - "fill booking form for van"
            - "submit booking"
            - "reset form"
            - "validate empty form"
            
            **Information:**
            - "check SUV pricing"
            - "check luxury car details"
            - "test contact links"
            """)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🎤 Natural Language Input")
        
        # Text input for custom commands
        user_input = st.text_area(
            "What would you like to automate?",
            placeholder="E.g., 'fill booking form for van', 'search for BMW', 'check SUV pricing'",
            height=100,
            key="user_input"
        )
        
        # Action buttons
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            if st.button("🚀 Execute Automation", type="primary", use_container_width=True):
                if user_input.strip():
                    execute_automation(user_input)
                else:
                    st.error("Please enter a command!")
        
        with col_btn2:
            if st.button("🧪 Test Command", use_container_width=True):
                if user_input.strip():
                    test_command(user_input)
                else:
                    st.error("Please enter a command!")
        
        with col_btn3:
            if st.button("🗑️ Clear History", use_container_width=True):
                st.session_state.automation_history = []
                st.session_state.screenshots = []
                st.success("History cleared!")
                st.rerun()
        
        # Current action status
        if st.session_state.current_action:
            st.markdown(f"""
            <div class="info-box">
                <strong>🔄 Current Action:</strong> {st.session_state.current_action}
            </div>
            """, unsafe_allow_html=True)
        
        # Advanced form for custom booking
        with st.expander("🔧 Advanced Booking Form"):
            st.subheader("Custom Booking Parameters")
            
            col_form1, col_form2 = st.columns(2)
            
            with col_form1:
                custom_name = st.text_input("Name", value="Keerthana")
                custom_email = st.text_input("Email", value="keer@example.com")
                car_type = st.selectbox("Car Type", ["VAN", "SUV", "Luxury"])
            
            with col_form2:
                start_date = st.date_input("Start Date", value=date(2025, 8, 1))
                end_date = st.date_input("End Date", value=date(2025, 8, 7))
                cdw_insurance = st.checkbox("CDW Insurance", value=True)
                accept_terms = st.checkbox("Accept Terms", value=True)
            
            if st.button("📝 Fill Custom Booking Form", use_container_width=True):
                custom_form_data = {
                    "action": "fill_booking_form",
                    "form_data": {
                        "name": custom_name,
                        "email": custom_email,
                        "start_date": start_date.strftime("%Y-%m-%d"),
                        "end_date": end_date.strftime("%Y-%m-%d"),
                        "car_type": car_type,
                        "cdw": cdw_insurance,
                        "terms": accept_terms
                    }
                }
                execute_direct_action(custom_form_data)
    
    with col2:
        st.header("📊 Status & Screenshots")
        
        # Screenshots section
        if st.session_state.screenshots:
            st.subheader("📸 Latest Screenshots")
            for i, screenshot in enumerate(reversed(st.session_state.screenshots[-3:])):  # Show last 3
                try:
                    # Convert bytes to image
                    image = Image.open(BytesIO(screenshot['image']))
                    st.image(image, caption=f"{screenshot['timestamp']} - {screenshot['action']}", use_column_width=True)
                except Exception as e:
                    st.error(f"Error displaying screenshot: {e}")
        else:
            st.info("📸 Screenshots will appear here after running automation")
    
    # History section
    st.header("📋 Automation History")
    
    if st.session_state.automation_history:
        for i, entry in enumerate(reversed(st.session_state.automation_history[-10:])):  # Show last 10
            with st.expander(f"🕐 {entry['timestamp']} - {entry['command'][:50]}{'...' if len(entry['command']) > 50 else ''}"):
                col_hist1, col_hist2 = st.columns(2)
                
                with col_hist1:
                    st.markdown("**Command:**")
                    st.code(entry['command'], language="text")
                    
                    st.markdown("**Status:**")
                    if entry['status'] == 'success':
                        st.success(f"✅ {entry['result']}")
                    else:
                        st.error(f"❌ {entry['result']}")
                
                with col_hist2:
                    st.markdown("**Parsed Action:**")
                    if entry['parsed_action']:
                        st.json(entry['parsed_action'])
                    else:
                        st.text("No parsed action")
                    
                    if 'screenshot' in entry and entry['screenshot']:
                        st.markdown("**Screenshot:**")
                        try:
                            image = Image.open(BytesIO(entry['screenshot']))
                            st.image(image, use_column_width=True)
                        except Exception as e:
                            st.error(f"Error displaying screenshot: {e}")
    else:
        st.info("📝 No automation history yet. Try running some commands!")

def test_command(user_input):
    """Test a command without executing it"""
    with st.spinner("🧪 Testing command..."):
        try:
            # Get Ollama response
            ollama_output = call_ollama_model(user_input)
            
            if not ollama_output:
                st.error("❌ No response from Ollama model")
                return
            
            # Parse response
            parsed_instruction = parse_response(ollama_output)
            
            if not parsed_instruction:
                st.error("❌ Could not parse instruction")
                with st.expander("Raw Ollama Output"):
                    st.code(ollama_output)
                return
            
            # Show results
            st.success("✅ Command parsed successfully!")
            
            col_test1, col_test2 = st.columns(2)
            
            with col_test1:
                st.markdown("**Raw Ollama Output:**")
                st.code(ollama_output, language="text")
            
            with col_test2:
                st.markdown("**Parsed Instruction:**")
                st.json(parsed_instruction)
                
        except Exception as e:
            st.error(f"❌ Error testing command: {str(e)}")

def execute_automation(user_input):
    """Execute automation with full workflow"""
    st.session_state.current_action = user_input
    
    # Create containers for progress
    progress_container = st.container()
    
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
    
    try:
        # Step 1: Call Ollama
        status_text.text("🤖 Sending command to Ollama...")
        progress_bar.progress(20)
        time.sleep(0.5)
        
        ollama_output = call_ollama_model(user_input)
        
        if not ollama_output:
            st.error("❌ No response from Ollama model")
            log_automation(user_input, None, "error", "No response from Ollama model")
            return
        
        # Step 2: Parse response
        status_text.text("🔍 Parsing response...")
        progress_bar.progress(40)
        time.sleep(0.5)
        
        parsed_instruction = parse_response(ollama_output)
        
        if not parsed_instruction:
            st.error("❌ Could not parse instruction")
            log_automation(user_input, None, "error", "Could not parse instruction", ollama_output)
            return
        
        # Step 3: Execute action
        status_text.text("🎬 Executing automation...")
        progress_bar.progress(60)
        time.sleep(0.5)
        
        # Execute the action
        result, screenshot = execute_playwright_action(parsed_instruction)
        
        # Step 4: Complete
        status_text.text("✅ Automation completed!")
        progress_bar.progress(100)
        time.sleep(0.5)
        
        # Log success
        log_automation(user_input, parsed_instruction, "success", result, ollama_output, screenshot)
        
        st.success(f"✅ Automation completed: {result}")
        
        # Clean up progress indicators
        time.sleep(1)
        progress_container.empty()
        
    except Exception as e:
        st.error(f"❌ Error during automation: {str(e)}")
        log_automation(user_input, parsed_instruction if 'parsed_instruction' in locals() else None, "error", str(e))
        progress_container.empty()
    
    finally:
        st.session_state.current_action = None

def execute_direct_action(action_dict):
    """Execute a direct action dictionary"""
    try:
        result, screenshot = execute_playwright_action(action_dict)
        st.success(f"✅ Action completed: {result}")
        log_automation("Direct custom action", action_dict, "success", result, None, screenshot)
    except Exception as e:
        st.error(f"❌ Error executing action: {str(e)}")
        log_automation("Direct custom action", action_dict, "error", str(e))

def execute_playwright_action(instruction):
    """Execute playwright action and handle screenshots"""
    try:
        result, screenshot = perform_action(instruction)
        
        if screenshot:
            # Store screenshot in session state
            screenshot_entry = {
                'image': screenshot,
                'action': instruction.get('action', 'unknown'),
                'timestamp': datetime.now().strftime("%H:%M:%S")
            }
            st.session_state.screenshots.append(screenshot_entry)
            
            # Keep only last 10 screenshots
            if len(st.session_state.screenshots) > 10:
                st.session_state.screenshots = st.session_state.screenshots[-10:]
        
        return result, screenshot
        
    except Exception as e:
        st.error(f"Error in playwright action: {e}")
        return str(e), None

def log_automation(command, parsed_action, status, result, raw_output=None, screenshot=None):
    """Log automation attempt to history"""
    entry = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'command': command,
        'parsed_action': parsed_action,
        'status': status,
        'result': result,
        'raw_output': raw_output
    }
    
    # Add screenshot if available
    if screenshot:
        entry['screenshot'] = screenshot
    
    st.session_state.automation_history.append(entry)
    
    # Keep only last 50 entries
    if len(st.session_state.automation_history) > 50:
        st.session_state.automation_history = st.session_state.automation_history[-50:]

# Add footer
def add_footer():
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        🚗 Car Rental Automation Tool | Powered by Playwright & Ollama tinyllama
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    add_footer()