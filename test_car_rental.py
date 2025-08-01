import pytest
import time
import re
from playwright.sync_api import Page, expect, BrowserContext


class TestInfyCarRentApplication:
    BASE_URL = 'https://automationdemo.vercel.app/'

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup method that runs before each test"""
        page.goto(self.BASE_URL)
        page.wait_for_timeout(3000)

    def test_should_load_homepage_with_correct_title_and_navigation(self, page: Page):
        """Test homepage loading with correct title and navigation"""
        # Check page title
        expect(page).to_have_title(re.compile(r"Car Rental"))
        
        # Check main heading
        expect(page.locator('h1.welcome')).to_have_text('Welcome to InfyCar Rent')
        
        # Check navigation links
        expect(page.locator('nav.navbar a[href="#home"]')).to_have_text('Home')
        expect(page.locator('nav.navbar a[href="#cars"]')).to_have_text('Available Cars')
        expect(page.locator('nav.navbar a[href="#price"]')).to_have_text('Pricing')
        expect(page.locator('nav.navbar a[href="#booking"]')).to_have_text('Booking Form')
        expect(page.locator('nav.navbar a[href="#contact"]')).to_have_text('Contact Us')
        
        # Check logo
        expect(page.locator('img.logo')).to_be_visible()
        
        # Check hero image
        expect(page.locator('img.hero-image')).to_be_visible()

    def test_should_test_search_bar_functionality(self, page: Page):
        """Test search bar functionality"""
        # Locate search input and button
        search_input = page.locator('form.search-bar input[name="search"]')
        search_button = page.locator('form.search-bar button')
        
        expect(search_input).to_be_visible()
        expect(search_button).to_be_visible()
        expect(search_input).to_have_attribute('placeholder', 'Search cars...')
        
        # Test search functionality
        search_input.fill('BMW')
        
        # Listen for new page opening
        with page.context.expect_page() as new_page_info:
            search_button.click()
        new_page = new_page_info.value
        
        # Verify new page opens with Wikipedia search
        expect(new_page).to_have_url(re.compile(r"wikipedia\.org"))
        new_page.close()


    def test_should_display_available_cars_section_correctly(self, page: Page):
        """Test available cars section display"""
        # Navigate to cars section
        page.locator('a[href="#cars"]').click()
        page.wait_for_timeout(500)
        
        # Check section heading
        expect(page.locator('#cars h2')).to_have_text('Available Cars')
        
        # Check car items
        car_items = page.locator('.car-item')
        expect(car_items).to_have_count(3)
        
        # Check SUV details
        suv_item = car_items.nth(0)
        expect(suv_item.locator('p')).to_have_text('SUV')
        expect(suv_item.locator('li').nth(0)).to_contain_text('4-5 doors')
        expect(suv_item.locator('li').nth(1)).to_contain_text('4 people')
        expect(suv_item.locator('li').nth(2)).to_contain_text('4 piece of laggae')
        
        # Check VAN details
        van_item = car_items.nth(1)
        expect(van_item.locator('p')).to_have_text('VAN')
        expect(van_item.locator('li').nth(1)).to_contain_text('8 people')
        expect(van_item.locator('li').nth(2)).to_contain_text('5-6 pices of luggage')
        
        # Check Luxury details
        luxury_item = car_items.nth(2)
        expect(luxury_item.locator('p')).to_have_text('Luxury')
        expect(luxury_item.locator('li').nth(2)).to_contain_text('2-3 pices of luggage')

    def test_should_display_pricing_table_correctly(self, page: Page):
        """Test pricing table display"""
        # Navigate to pricing section
        page.locator('a[href="#price"]').click()
        page.wait_for_timeout(500)
        
        # Check section heading
        expect(page.locator('#price h2')).to_have_text('Pricing Section')
        
        # Check table headers
        expect(page.locator('th').nth(0)).to_have_text('Car Type')
        expect(page.locator('th').nth(1)).to_have_text('Price Per Day')
        expect(page.locator('th').nth(2)).to_have_text('Price Per Week')
        expect(page.locator('th').nth(3)).to_have_text('Notes')
        
        # Check table data
        rows = page.locator('tbody tr')
        expect(rows).to_have_count(3)
        
        # Check SUV row
        expect(rows.nth(0).locator('td').nth(0)).to_have_text('SUV')
        expect(rows.nth(0).locator('td').nth(1)).to_have_text('$22')
        expect(rows.nth(0).locator('td').nth(2)).to_have_text('$154')
        expect(rows.nth(0).locator('td').nth(3)).to_have_text('Available is different color')
        
        # Check VAN row
        expect(rows.nth(1).locator('td').nth(0)).to_have_text('VAN')
        expect(rows.nth(1).locator('td').nth(1)).to_have_text('$35')
        expect(rows.nth(1).locator('td').nth(2)).to_have_text('$235')
        
        # Check Luxury row
        expect(rows.nth(2).locator('td').nth(0)).to_have_text('Luxury')
        expect(rows.nth(2).locator('td').nth(1)).to_have_text('$48')
        expect(rows.nth(2).locator('td').nth(2)).to_have_text('$322')

    def test_should_test_form_validation_with_empty_fields(self, page: Page):
        """Test form validation with empty fields"""
        # Navigate to booking section
        page.locator('a[href="#booking"]').click()
        page.wait_for_timeout(500)
        
        submit_button = page.locator('#submit')
        
        # Handle alert dialog for validation
        def handle_dialog(dialog):
            assert 'Please fill in all required fields' in dialog.message
            dialog.accept()
        
        page.on('dialog', handle_dialog)
        
        # Try to submit empty form
        submit_button.click()

    def test_should_test_form_submission_with_valid_data(self, page: Page):
        """Test form submission with valid data"""
        # Navigate to booking section
        page.locator('a[href="#booking"]').click()
        page.wait_for_timeout(500)
        
        # Fill all required fields
        page.locator('#fn').fill('John Doe')
        page.locator('#email').fill('john.doe@example.com')
        page.locator('input[name="start"]').fill('2025-08-01')
        page.locator('input[name="end"]').fill('2025-08-07')
        page.locator('#type').select_option('VAN')
        page.locator('#cdw').check()
        page.locator('#term1').check()
        
        # Test form submission (opens new tab)
        with page.context.expect_page() as new_page_info:
            page.locator('#submit').click()
        new_page = new_page_info.value
        
        # Verify new page opens
        expect(new_page).to_have_url(re.compile(r'submit\.html'))
        new_page.close()

    def test_should_test_reset_button_functionality(self, page: Page):
        """Test reset button functionality"""
        # Navigate to booking section
        page.locator('a[href="#booking"]').click()
        page.wait_for_timeout(500)
        
        # Fill some fields
        page.locator('#fn').fill('Test User')
        page.locator('#email').fill('test@example.com')
        page.locator('#type').select_option('Luxury')
        page.locator('#cdw').check()
        page.locator('#term1').check()
        
        # Click reset button
        page.locator('#reset').click()
        
        # Verify fields are cleared
        expect(page.locator('#fn')).to_have_value('')
        expect(page.locator('#email')).to_have_value('')
        expect(page.locator('#type')).to_have_value('')
        expect(page.locator('#cdw')).not_to_be_checked()
        expect(page.locator('#term1')).not_to_be_checked()

    def test_should_test_footer_contact_links(self, page: Page):
        """Test footer contact links"""
        # Scroll to footer
        page.locator('#contact').scroll_into_view_if_needed()
        
        # Check footer elements
        expect(page.locator('.footer-section h4')).to_have_text('Contact Us')
        expect(page.locator('.footer-section p')).to_have_text('@2025 InfyFood')
        
        # Test contact links
        contact_links = page.locator('.footer-section a')
        expect(contact_links).to_have_count(4)
        
        # Test email link click
        def handle_dialog(dialog):
            assert 'infycar' in dialog.message
            dialog.accept()
        
        page.on('dialog', handle_dialog)
        contact_links.nth(0).click()

    def test_should_test_google_maps_iframe(self, page: Page):
        """Test Google Maps iframe"""
        # Check if map iframe is present
        map_iframe = page.locator('section.map iframe')
        expect(map_iframe).to_be_visible()
        expect(map_iframe).to_have_attribute('src', re.compile(r'maps\.google\.com'))
        expect(map_iframe).to_have_attribute('width', '100%')
        expect(map_iframe).to_have_attribute('height', '300')

    def test_should_test_navigation_anchor_links(self, page: Page):
        """Test navigation anchor links"""
        # Test navigation links scroll to sections
        page.locator('a[href="#cars"]').click()
        page.wait_for_timeout(500)
        expect(page.locator('#cars')).to_be_in_viewport()
        
        page.locator('a[href="#price"]').click()
        page.wait_for_timeout(500)
        expect(page.locator('#price')).to_be_in_viewport()
        
        page.locator('a[href="#booking"]').click()
        page.wait_for_timeout(500)
        expect(page.locator('#booking')).to_be_in_viewport()
        
        page.locator('a[href="#contact"]').click()
        page.wait_for_timeout(500)
        expect(page.locator('#contact')).to_be_in_viewport()
        
        page.locator('a[href="#home"]').click()
        page.wait_for_timeout(500)
        expect(page.locator('#home')).to_be_in_viewport()

    # def test_should_test_responsive_design(self, page: Page):
    #     """Test responsive design"""
    #     # Test desktop view
    #     page.set_viewport_size({"width": 1280, "height": 720})
    #     expect(page.locator('h1.welcome')).to_be_visible()
    #     expect(page.locator('nav.navbar')).to_be_visible()
        
    #     # Test tablet view
    #     page.set_viewport_size({"width": 768, "height": 1024})
    #     expect(page.locator('h1.welcome')).to_be_visible()
        
    #     # Test mobile view
    #     page.set_viewport_size({"width": 375, "height": 667})
    #     expect(page.locator('h1.welcome')).to_be_visible()


class TestPerformance:
    """Performance tests"""
    BASE_URL = 'https://automationdemo.vercel.app/'

    def test_should_load_page_within_acceptable_time(self, page: Page):
        """Test page load performance"""
        start_time = time.time() * 1000  # Convert to milliseconds
        page.goto(self.BASE_URL)
        page.wait_for_load_state('networkidle')
        load_time = time.time() * 1000 - start_time
        
        print(f"Page load time: {load_time:.0f}ms")
        assert load_time < 10000, f"Page load time {load_time:.0f}ms exceeds 10 seconds"
        
        # Check if main elements are loaded
        expect(page.locator('h1.welcome')).to_be_visible()
        expect(page.locator('nav.navbar')).to_be_visible()