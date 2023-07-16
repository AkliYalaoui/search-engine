from selenium import webdriver


def css_color_to_rgb(css_color):
    if css_color.startswith('rgba'):
        # Remove 'rgba(' and ')' and split by comma
        color_values = css_color[5:-1].split(',')
        # Extract the RGB components and alpha
        rgb = [int(value.strip()) for value in color_values[:3]]
        alpha = float(color_values[3].strip())
        # Convert the alpha value to opacity
        rgb.append(int(alpha * 255))
        return rgb
    elif css_color.startswith('rgb'):
        # Remove 'rgb(' and ')' and split by comma
        color_values = css_color[4:-1].split(',')
        # Convert string values to integers
        rgb = [int(value.strip()) for value in color_values]
        return rgb
    else:
        raise ValueError("Invalid CSS color format: " + css_color)
    
def calculate_contrast_ratio(background_rgba, foreground_rgba):
    # Convert the colors to normalized RGBA format
    background_rgba = [channel / 255 for channel in background_rgba]
    foreground_rgba = [channel / 255 for channel in foreground_rgba]
    
    # Convert the colors to relative luminance
    background_luminance = calculate_relative_luminance(background_rgba)
    foreground_luminance = calculate_relative_luminance(foreground_rgba)
    
    # Calculate the contrast ratio
    contrast_ratio = (max(background_luminance, foreground_luminance) + 0.05) / (min(background_luminance, foreground_luminance) + 0.05)
    return contrast_ratio

def calculate_relative_luminance(rgba):
    # Convert RGBA values to relative luminance using the sRGB formula
    r, g, b, a = rgba
    r_linear = gamma_correction(r)
    g_linear = gamma_correction(g)
    b_linear = gamma_correction(b)
    luminance = 0.2126 * r_linear + 0.7152 * g_linear + 0.0722 * b_linear
    return luminance

def gamma_correction(component):
    if component <= 0.03928:
        return component / 12.92
    else:
        return ((component + 0.055) / 1.055) ** 2.4
    

def get_contrast_ratio(url):

    try : 
        # Set up Selenium Chrome WebDriver
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode
        driver = webdriver.Chrome(options=options)
        
        # Load the web page
        driver.get(url)
        
        # Find the body element
        body_element = driver.execute_script('return document.body')
        
        # Get the computed background and foreground colors
        background_color = body_element.value_of_css_property('background-color')
        foreground_color = body_element.value_of_css_property('color')
        
        # Close the WebDriver
        driver.quit()
        
        if background_color and  foreground_color:
            # Convert the colors to RGB format
            background_rgb = css_color_to_rgb(background_color)
            foreground_rgb = css_color_to_rgb(foreground_color)

            print("background_rgb", background_rgb)
            print("foreground_rgb", foreground_rgb)

            # Calculate the contrast ratio using skimage
            contrast_ratio = calculate_contrast_ratio(background_rgb, foreground_rgb)
            print("contrast_ratio", contrast_ratio)
            return contrast_ratio

        else :
            print("contrast_ratio", " 'Unable to extract colors from CSS'")
            return 0
    except Exception as e : 
        print(e)
        return 0
    

if __name__ == "__main__" :
    test_url = "https://baleares.craigslist.org/"
    get_contrast_ratio(test_url)