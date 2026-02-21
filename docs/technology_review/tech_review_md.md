# Technology Review

Technology Review: Python Web Frameworks for Data Tools

### 1. Background

Our project requires a user interface that allows for interactive recipe searching, ZIP-code-based location filtering, and dynamic pricing displays using the Kroger Development API. Therefore, we need a framework that can handle:

User Inputs: Real-time text search and ZIP code entry.

API Integration: Secure handling of OAuth2 tokens and asynchronous product queries.

Data Visualization: Clear, interactive display of grocery prices and the ingredients for the recipe.

### 2. Technology Candidates

**Streamlit**

Author: Snowflake (formerly Streamlit Inc.)

Summary: An open-source Python library that turns data scripts into shareable web apps in minutes. It uses a declarative, top-down execution model where the entire script reruns every time a user interacts with a widget.

Target Audience: Data scientist focused on rapid prototyping.

Pros of using Streamlit: Simple to use, great for small-scale app development, might be more intuitive to use.

Cons: Less customization features.

**Plotly Dash**

Author: Plotly

Summary: A productive Python framework for building analytical web applications. It is built on top of Flask (web server), Plotly.js (charts), and React.js (UI). It uses an event-driven model with explicit callbacks.

Target Audience: Data scientists building complex, scalable, or highly customized dashboards.

Pros of using Plotly Dash: Highly customizable, great for larger datasets.

Cons of using Plotly Dash: More complex to use, more integration with HTML and CSS. 
