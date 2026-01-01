# Smart Doc Generator (Dify Plugin)

A smart Markdown to Word document generator with **automatic chart generation** (pie charts, bar charts, line charts) and flexible template mechanism, enabling rapid generation of formatted Word documents with rich visualizations for various scenarios.

## Overview

Smart Doc Generator is a powerful Dify plugin that converts Markdown content into professionally formatted Word documents (.docx). **The plugin's standout feature is its intelligent chart generation system** that automatically recognizes data patterns in Markdown and generates beautiful, professional charts (pie charts, bar charts, line charts) directly embedded in Word documents. Combined with a flexible template system, it enables rapid generation of data-rich, visually appealing documents.

## Key Features

### 📊 Intelligent Chart Generation (Core Feature)

**Generate professional charts directly in Word documents!** This plugin's most powerful feature automatically creates beautiful, publication-ready charts from your data:

- **Automatic Chart Recognition**: Intelligently identifies data patterns in Markdown tables and content
- **Multiple Chart Types**: Supports pie charts, bar charts, and line charts
- **Flexible Positioning**: Charts can be inserted at specific positions in the document (before/after headings, tables, etc.)
- **Professional Styling**: Charts are styled to match your document theme and color scheme
- **Customizable Size**: Adjust chart width to fit your document layout
- **Seamless Integration**: Charts are embedded directly in the Word document, no external files needed

**Use Cases:**
- Sales reports with monthly trend charts
- Survey results with pie chart visualizations
- Performance dashboards with bar chart comparisons
- Research papers with data visualization
- Business presentations with embedded charts

### 🎨 Template System (Core Feature)

This plugin uses a **dual-layer template architecture** providing a highly customizable document styling system:

- **Theme**: Defines the overall visual style and color scheme of the document
- **Style Template**: Defines specific styles for fonts, paragraphs, tables, and other elements
- **Style Overrides**: Themes can override specific settings in style templates

With the template system, you can:
- Quickly switch between different document styles (academic, business, minimal, etc.)
- Reuse style configurations to maintain document consistency
- Flexibly customize to meet specific scenario requirements

### Other Features

- ✅ Markdown → Word (.docx) conversion
- ✅ Configurable fonts, font sizes, line spacing, page margins, etc.
- ✅ Support for page numbers, headers, and footers
- ✅ Returns document files and JSON metadata
- ✅ Rich element support: tables, code blocks, quotes, etc.

## Template System Architecture

### Directory Structure

```
src/templates/
├── themes/
│   └── theme_config.yaml      # Theme configuration file
└── styles/
    ├── default.yaml            # Default style template
    ├── academic.yaml           # Academic style template
    └── business.yaml           # Business style template
```

### Template Hierarchy

```
Theme
  ├── References style template (style_template)
  ├── Defines color scheme (color_scheme)
  └── Style overrides (overrides)
      └── Overrides specific settings in style template
```

### Built-in Themes

The system includes multiple predefined themes ready to use:

| Theme Name | Use Case | Characteristics |
|-----------|----------|----------------|
| `default` | System alerts, monitoring reports | Formal, professional, red color scheme |
| `academic` | Academic papers | Times New Roman font, double spacing |
| `business` | Business reports | Calibri font, modern business style |
| `minimal` | Technical documents | Minimalist style, Helvetica font |
| `dark` | Dark theme documents | Dark background, suitable for presentations |
| `colorful` | Colorful documents | Rich and colorful color scheme |

## Installation

### Prerequisites

- Python 3.12
- A running Dify instance
- Dify Plugin SDK (installed automatically with the plugin)

### Installation Steps

1. **Download the Plugin Package**
   - Download the `.difypkg` file from the releases page
   - Or build it yourself using the Dify CLI tool (see Building section)

2. **Install in Dify**
   - Open your Dify instance
   - Navigate to **Settings** → **Plugins**
   - Click **Install Plugin**
   - Upload the `.difypkg` file
   - Wait for installation to complete

3. **Verify Installation**
   - The plugin should appear in your plugins list
   - You can now use it in your workflows

### Building from Source

If you want to build the plugin package yourself:

1. **Install Dify CLI Tool**
   ```bash
   wget https://github.com/langgenius/dify-plugin-daemon/releases/download/0.0.6/dify-plugin-linux-amd64
   chmod +x dify-plugin-linux-amd64
   ```

2. **Package the Plugin**
   ```bash
   ./dify-plugin-linux-amd64 plugin package . -o smart_doc_generator-1.0.0.difypkg
   ```

## Usage

### Basic Usage

In a Dify workflow, simply provide Markdown text and select a template:

```yaml
markdown_text: "# Title\n\nThis is the body content..."
templates: "default"  # Use default theme
```

### Tool Parameters

All parameters are defined in `tools/markdown_to_word.yaml`:

#### Required Parameters

- **markdown_text** (string, required): The Markdown content to convert

#### Optional Parameters

- **templates** (string, optional): Theme/template name, default `"default"`
  - Available values: `default`, `academic`, `business`, `minimal`, `dark`, `colorful`
  
- **font_family** (string, optional): Font family, default `"Microsoft YaHei"`
  - Common values: `"Microsoft YaHei"`, `"SimSun"`, `"Times New Roman"`, `"Calibri"`, `"Helvetica"`
  
- **font_size** (number, optional): Body font size, default `12`
  - Recommended range: 10-18
  
- **line_spacing** (number, optional): Line spacing, default `1.5`
  - Common values: `1.0`, `1.5`, `2.0`
  
- **page_margins** (number, optional): Page margins in centimeters, default `2.5`
  - Recommended range: 2.0-4.0, same for all sides
  
- **paper_size** (string, optional): Paper size, default `"A4"`
  - Available values: `"A4"`, `"A3"`, `"Letter"`
  
- **output_file** (string, optional): Output file name, default `"output.docx"`
  
- **enable_charts** (boolean, optional): Enable automatic chart generation, default `false`
  
- **chart_data** (string, optional): Processed chart data in JSON format
  - Expected format: `{"charts": [{"type": "pie"|"bar"|"line", "title": "...", "position": "after:...", "data": {...}}]}`
  
- **chart_insert_width** (number, optional): Chart width in centimeters when inserted, default `14.0`

### Output Results

The tool returns two messages:

1. **File (BLOB)**: Generated Word document (.docx)
   - Appears in the workflow result's `files` field
   - Can be downloaded directly
   - MIME type: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`

2. **JSON Metadata**: Contains conversion result summary
   ```json
   {
     "result": "success",
     "output_file": "output.docx",
     "file_size": 12345,
     "settings": {
       "template": "default",
       "font_family": "Microsoft YaHei",
       "font_size": 12,
       ...
     }
   }
   ```

## Chart Generation Guide

### How Chart Generation Works

The chart generation feature allows you to automatically insert professional charts into your Word documents. Here's how it works:

1. **Enable Chart Generation**: Set `enable_charts: true` in your tool parameters
2. **Provide Chart Data**: Pass chart data in JSON format via the `chart_data` parameter
3. **Specify Chart Position**: Define where charts should appear in the document using the `position` field
4. **Automatic Rendering**: The plugin generates the chart image and inserts it into the Word document

### Chart Data Format

The `chart_data` parameter accepts a JSON object with the following structure:

```json
{
  "charts": [
    {
      "type": "pie" | "bar" | "line",
      "title": "Chart Title",
      "position": "after:Heading Text" | "before:Heading Text" | "after:Table Title",
      "data": {
        "Label1": value1,
        "Label2": value2,
        ...
      }
    }
  ]
}
```

### Chart Types

#### Pie Charts
Perfect for showing proportions and percentages:
```json
{
  "type": "pie",
  "title": "Market Share",
  "position": "after:Market Analysis",
  "data": {
    "Product A": 35,
    "Product B": 25,
    "Product C": 40
  }
}
```

#### Bar Charts
Ideal for comparing values across categories:
```json
{
  "type": "bar",
  "title": "Monthly Sales",
  "position": "after:Sales Data",
  "data": {
    "Jan": 1000,
    "Feb": 1500,
    "Mar": 1200
  }
}
```

#### Line Charts
Great for showing trends over time:
```json
{
  "type": "line",
  "title": "Revenue Trend",
  "position": "after:Financial Overview",
  "data": {
    "Q1": 50000,
    "Q2": 55000,
    "Q3": 60000,
    "Q4": 65000
  }
}
```

### Chart Positioning

Charts can be positioned relative to document elements:
- `"after:Heading Text"` - Inserts chart after the first occurrence of the specified heading
- `"before:Heading Text"` - Inserts chart before the specified heading
- `"after:Table Title"` - Inserts chart after a table with the specified title

## Examples

### Example 1: Generating Word Document with Charts

```yaml
markdown_text: |
  # Sales Report Q4 2024
  
  ## Monthly Sales Data
  
  | Month | Sales | Growth |
  |-------|-------|--------|
  | Oct   | 1000  | +10%   |
  | Nov   | 1500  | +50%   |
  | Dec   | 1800  | +20%   |
  
  ## Product Distribution
  
  Our products are distributed across three main categories.

templates: "business"
enable_charts: true
chart_data: |
  {
    "charts": [
      {
        "type": "bar",
        "title": "Monthly Sales Trend",
        "position": "after:Monthly Sales Data",
        "data": {
          "Oct": 1000,
          "Nov": 1500,
          "Dec": 1800
        }
      },
      {
        "type": "pie",
        "title": "Product Distribution",
        "position": "after:Product Distribution",
        "data": {
          "Category A": 45,
          "Category B": 30,
          "Category C": 25
        }
      }
    ]
  }
chart_insert_width: 14.0
```

### Example 2: Using Default Theme

```yaml
markdown_text: |
  # System Alert Report
  
  ## Alert Overview
  
  This report contains system monitoring alert information.
  
  | Alert Level | Count |
  |------------|-------|
  | Critical   | 5     |
  | Warning    | 10    |

templates: "default"
add_page_numbers: true
```

### Example 3: Using Academic Theme

```yaml
markdown_text: |
  # Research Paper Title
  
  ## Abstract
  
  This paper presents...
  
  ## Introduction
  
  ...

templates: "academic"
font_family: "Times New Roman"
line_spacing: 2.0
```

### Example 4: Using Business Theme with Customization

```yaml
markdown_text: |
  # Business Report
  
  ## Executive Summary
  
  ...

templates: "business"
font_size: 11
page_margins: 2.0
paper_size: "A4"
```

### Example 5: Complex Report with Multiple Charts

```yaml
markdown_text: |
  # Annual Performance Report 2024
  
  ## Revenue Overview
  
  Our revenue has shown consistent growth throughout the year.
  
  | Quarter | Revenue | Profit |
  |---------|---------|--------|
  | Q1      | 50000   | 10000  |
  | Q2      | 55000   | 12000  |
  | Q3      | 60000   | 14000  |
  | Q4      | 65000   | 15000  |
  
  ## Market Share Analysis
  
  We have maintained a strong position in the market.
  
  ## Regional Performance
  
  Performance varies across different regions.

templates: "business"
enable_charts: true
chart_data: |
  {
    "charts": [
      {
        "type": "line",
        "title": "Revenue Trend 2024",
        "position": "after:Revenue Overview",
        "data": {
          "Q1": 50000,
          "Q2": 55000,
          "Q3": 60000,
          "Q4": 65000
        }
      },
      {
        "type": "pie",
        "title": "Market Share Distribution",
        "position": "after:Market Share Analysis",
        "data": {
          "Our Company": 35,
          "Competitor A": 25,
          "Competitor B": 20,
          "Others": 20
        }
      },
      {
        "type": "bar",
        "title": "Regional Performance",
        "position": "after:Regional Performance",
        "data": {
          "North": 30000,
          "South": 25000,
          "East": 35000,
          "West": 20000
        }
      }
    ]
  }
chart_insert_width: 15.0
```

## Template Configuration

### Theme Configuration File

Theme configuration is located in `src/templates/themes/theme_config.yaml`:

```yaml
themes:
  default:
    name: "Default Theme"
    description: "Formal theme suitable for system alerts and monitoring reports"
    style_template: "default.yaml"  # Referenced style template
    color_scheme:
      primary: "#d32f2f"      # Primary color
      secondary: "#ff9800"    # Secondary color
      accent: "#2196f3"       # Accent color
      background: "#ffffff"   # Background color
      text: "#333333"         # Text color
      border: "#424242"       # Border color
    
    # Custom style overrides
    overrides:
      fonts:
        body:
          name: "Microsoft YaHei"
          size: 11
      headings:
        h1:
          color: "#1a1a1a"
          border_color: "#d32f2f"
      table:
        header_background: "#f44336"
        header_font_color: "#ffffff"
```

### Style Template Files

Style templates are located in the `src/templates/styles/` directory:

```yaml
# Page settings
page:
  width: 21.0      # cm
  height: 29.7     # cm
  margin_top: 2.5  # cm
  margin_bottom: 2.5
  margin_left: 3.0
  margin_right: 2.5
  orientation: "portrait"

# Font settings
fonts:
  body:
    name: "SimSun"
    size: 14
    color: "#000000"
  
  heading:
    name: "SimSun"
    size: 16
    bold: true

# Paragraph settings
paragraph:
  line_spacing: 28  # 28pt fixed line spacing
  space_before: 0
  space_after: 0
  alignment: "left"

# Heading styles
headings:
  h1:
    font_size: 22
    font_name: "SimSun"
    alignment: "center"
    line_spacing: 1.25
  
  h2:
    font_size: 16
    font_name: "SimHei"
    bold: true

# Table styles
table:
  border_width: 1.0
  border_color: "#424242"
  header_background: "#f44336"
  header_font_color: "#ffffff"
  alternate_row_color: "#fff3e0"

# Code block styles
code_block:
  background_color: "#f5f5f5"
  border_color: "#d32f2f"
  font_family: "Consolas"
  font_size: 9
```

## Custom Templates

### Creating a New Theme

1. **Edit Theme Configuration**: Add a new theme in `src/templates/themes/theme_config.yaml`:

```yaml
themes:
  my_custom_theme:
    name: "My Custom Theme"
    description: "Theme suitable for my business scenario"
    style_template: "default.yaml"  # Can reuse existing style template
    color_scheme:
      primary: "#0066cc"
      secondary: "#666666"
      # ...
    overrides:
      fonts:
        body:
          name: "Microsoft YaHei"
          size: 12
      # Other override settings...
```

2. **Create New Style Template** (optional): If you need a completely new style configuration, create a new YAML file in the `src/templates/styles/` directory

3. **Use New Theme**: Specify the theme name when calling the tool:

```yaml
templates: "my_custom_theme"
```

## Troubleshooting

- If Dify results show an empty `files` array, ensure your environment uses a plugin version that supports file BLOB returns (this project already supports it)
- Very large Markdown inputs may require longer conversion times
- When customizing themes, ensure YAML format is correct to avoid syntax errors
- Font names must be installed on the system, otherwise default fonts will be used
- Color values in style templates use hexadecimal format (e.g., `#d32f2f`)

## Template System Advantages

1. **Flexibility**: Through theme and style template separation, achieve highly flexible style customization
2. **Maintainability**: Centralized style configuration management, easy to maintain and update
3. **Extensibility**: Easily add new themes and style templates without modifying core code
4. **Consistency**: Ensure document style consistency through templates
5. **Usability**: Predefined themes ready to use, lowering the barrier to entry

## Privacy

This plugin processes all data locally and does not collect or transmit any user data. For detailed privacy information, please see [PRIVACY.md](smart_doc_generator/PRIVACY.md).

## Requirements

- Python 3.12
- Dependencies: See `requirements.txt`
  - `dify_plugin>0.3.0`
  - `matplotlib==3.8.3`
  - `numpy`
  - `Pillow`
  - `markdown`
  - `python-docx`
  - `PyYAML`

## Development

### Debug Mode

1. Copy `.env.example` to `.env` and fill in necessary configuration values (Dify server remote installation URL and key)
2. Install dependencies: `pip install -r requirements.txt`
3. Start debug mode: `python -m main`
4. In Dify → Plugins, use debug connection to test the tool in workflows

## Contributing

Contributions are welcome! Please feel free to submit Issues and Pull Requests to improve the template system and functionality.

## License

[Specify your license here]

## Support

For issues, questions, or feature requests, please open an issue on the GitHub repository.
