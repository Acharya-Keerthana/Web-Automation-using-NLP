from playwright.sync_api import sync_playwright
import base64
from io import BytesIO
from PIL import Image
import os
from datetime import datetime

def perform_action (instruction):
    """Enhanced perform_action that captures and returns screenshots"""
    action = instruction.get("action")
    query = instruction.get("query")
    screenshots = []
    result_message = ""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://automationdemo.vercel.app/")
        
        # Wait for page to load
        page.wait_for_timeout(2000)
        
        # Take initial screenshot
        initial_screenshot = capture_screenshot(page, "Initial page load")
        screenshots.append(initial_screenshot)
        
        try:
            if action == "search_car":
                # Test search bar functionality
                search_input = page.locator('form.search-bar input[name="search"]')
                search_button = page.locator('form.search-bar button')
                
                # Fill search input
                search_input.fill(query)
                page.wait_for_timeout(500)
                
                # Take screenshot before search
                before_search = capture_screenshot(page, f"Before searching for '{query}'")
                screenshots.append(before_search)
                
                # Listen for new page opening
                with page.context.expect_page() as new_page_info:
                    search_button.click()
                new_page = new_page_info.value
                
                # Take screenshot of search results
                new_page.wait_for_timeout(2000)
                search_result = capture_screenshot(new_page, f"Search results for '{query}'")
                screenshots.append(search_result)
                
                result_message = f"Search completed for '{query}'. New page: {new_page.url}"
                new_page.close()
                
            elif action == "fill_booking_form":
                # Navigate to booking section
                page.locator('a[href="#booking"]').click()
                page.wait_for_timeout(1000)
                
                # Take screenshot of empty form
                empty_form = capture_screenshot(page, "Empty booking form")
                screenshots.append(empty_form)
                
                # Fill form with provided data
                form_data = instruction.get("form_data", {})
                page.locator('#fn').fill(form_data.get("name", "John Doe"))
                page.locator('#email').fill(form_data.get("email", "john@example.com"))
                page.locator('input[name="start"]').fill(form_data.get("start_date", "2025-08-01"))
                page.locator('input[name="end"]').fill(form_data.get("end_date", "2025-08-07"))
                page.locator('#type').select_option(form_data.get("car_type", "SUV"))
                
                if form_data.get("cdw", True):
                    page.locator('#cdw').check()
                if form_data.get("terms", True):
                    page.locator('#term1').check()
                
                page.wait_for_timeout(500)
                
                # Take screenshot of filled form
                filled_form = capture_screenshot(page, "Filled booking form")
                screenshots.append(filled_form)
                
                result_message = "Booking form filled successfully"
                
            elif action == "submit_booking":
                # Navigate to booking section
                page.locator('a[href="#booking"]').click()
                page.wait_for_timeout(1000)
                
                # Take screenshot before submit
                before_submit = capture_screenshot(page, "Before submitting booking")
                screenshots.append(before_submit)
                
                with page.context.expect_page() as new_page_info:
                    page.locator('#submit').click()
                new_page = new_page_info.value
                
                # Take screenshot of submission result
                new_page.wait_for_timeout(2000)
                submit_result = capture_screenshot(new_page, "Booking submission result")
                screenshots.append(submit_result)
                
                result_message = f"Booking submitted. Redirect page: {new_page.url}"
                new_page.close()
                
            elif action == "reset_form":
                # Navigate to booking section
                page.locator('a[href="#booking"]').click()
                page.wait_for_timeout(1000)
                
                # Take screenshot before reset
                before_reset = capture_screenshot(page, "Before form reset")
                screenshots.append(before_reset)
                
                page.locator('#reset').click()
                page.wait_for_timeout(500)
                
                # Take screenshot after reset
                after_reset = capture_screenshot(page, "After form reset")
                screenshots.append(after_reset)
                
                result_message = "Form reset completed"
                
            elif action == "navigate_to_section":
                section = instruction.get("section", "#home")
                
                # Take screenshot before navigation
                before_nav = capture_screenshot(page, f"Before navigating to {section}")
                screenshots.append(before_nav)
                
                page.locator(f'a[href="{section}"]').click()
                page.wait_for_timeout(1000)
                
                # Take screenshot after navigation
                after_nav = capture_screenshot(page, f"After navigating to {section}")
                screenshots.append(after_nav)
                
                result_message = f"Navigated to section: {section}"
                
            elif action == "test_contact_links":
                # Scroll to contact section
                page.locator('#contact').scroll_into_view_if_needed()
                page.wait_for_timeout(500)
                
                # Take screenshot of contact section
                contact_section = capture_screenshot(page, "Contact section")
                screenshots.append(contact_section)
                
                dialog_message = ""
                def handle_dialog(dialog):
                    nonlocal dialog_message
                    dialog_message = dialog.message
                    dialog.accept()
                
                page.on('dialog', handle_dialog)
                page.locator('.footer-section a').first.click()
                page.wait_for_timeout(1000)
                
                # Take screenshot after dialog
                after_dialog = capture_screenshot(page, "After contact dialog")
                screenshots.append(after_dialog)
                
                result_message = f"Contact link tested. Dialog: {dialog_message}"
                
            elif action == "check_pricing":
                # Navigate to pricing section
                page.locator('a[href="#price"]').click()
                page.wait_for_timeout(1000)
                
                # Take screenshot of pricing table
                pricing_table = capture_screenshot(page, "Pricing table")
                screenshots.append(pricing_table)
                
                car_type = instruction.get("car_type", "SUV")
                rows = page.locator('tbody tr')
                
                price_per_day = ""
                if car_type == "SUV":
                    price_per_day = rows.nth(0).locator('td').nth(1).text_content()
                elif car_type == "VAN":
                    price_per_day = rows.nth(1).locator('td').nth(1).text_content()
                elif car_type == "Luxury":
                    price_per_day = rows.nth(2).locator('td').nth(1).text_content()
                
                result_message = f"{car_type} price per day: {price_per_day}"
                
            elif action == "validate_empty_form":
                # Navigate to booking section
                page.locator('a[href="#booking"]').click()
                page.wait_for_timeout(1000)
                
                # Take screenshot of empty form
                empty_form = capture_screenshot(page, "Empty form for validation")
                screenshots.append(empty_form)
                
                validation_message = ""
                def handle_dialog(dialog):
                    nonlocal validation_message
                    validation_message = dialog.message
                    dialog.accept()
                
                page.on('dialog', handle_dialog)
                page.locator('#submit').click()
                page.wait_for_timeout(1000)
                
                # Take screenshot after validation
                after_validation = capture_screenshot(page, "After validation attempt")
                screenshots.append(after_validation)
                
                result_message = f"Empty form validation tested. Message: {validation_message}"
                
            elif action == "check_car_details":
                # Navigate to cars section
                page.locator('a[href="#cars"]').click()
                page.wait_for_timeout(1000)
                
                # Take screenshot of cars section
                cars_section = capture_screenshot(page, "Cars section")
                screenshots.append(cars_section)
                
                car_type = instruction.get("car_type", "SUV")
                car_items = page.locator('.car-item')
                
                car_name = ""
                if car_type == "SUV":
                    car_name = car_items.nth(0).locator('p').text_content()
                elif car_type == "VAN":
                    car_name = car_items.nth(1).locator('p').text_content()
                elif car_type == "Luxury":
                    car_name = car_items.nth(2).locator('p').text_content()
                
                result_message = f"Car type: {car_name}"
                
            else:
                result_message = f"Unsupported action: {action}"
                
        except Exception as e:
            error_screenshot = capture_screenshot(page, f"Error occurred: {str(e)}")
            screenshots.append(error_screenshot)
            result_message = f"Error: {str(e)}"
            
        finally:
            # Take final screenshot
            final_screenshot = capture_screenshot(page, "Final state")
            screenshots.append(final_screenshot)
            
            browser.close()
    
    # Return the most relevant screenshot (usually the last meaningful one)
    main_screenshot = screenshots[-2] if len(screenshots) > 1 else screenshots[0] if screenshots else None
    
    return result_message, main_screenshot

def capture_screenshot(page, description="Screenshot"):
    """Capture screenshot and return as base64 encoded image"""
    try:
        # Take screenshot as bytes
        screenshot_bytes = page.screenshot(full_page=True)
        
        # Convert to PIL Image
        image = Image.open(BytesIO(screenshot_bytes))
        
        # Resize if too large (optional)
        if image.width > 1200:
            ratio = 1200 / image.width
            new_height = int(image.height * ratio)
            image = image.resize((1200, new_height), Image.Resampling.LANCZOS)
        
        # Convert back to bytes
        img_buffer = BytesIO()
        image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        return img_buffer.getvalue()
        
    except Exception as e:
        print(f"Error capturing screenshot: {e}")
        return None

def save_screenshot_to_file(screenshot_bytes, filename):
    """Save screenshot to file (optional)"""
    try:
        os.makedirs("screenshots", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"screenshots/{timestamp}_{filename}.png"
        
        with open(filepath, "wb") as f:
            f.write(screenshot_bytes)
        
        return filepath
    except Exception as e:
        print(f"Error saving screenshot: {e}")
        return None