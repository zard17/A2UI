
# Registry of available UI templates for the Generic Chat Agent

TEMPLATES = {
    "SINGLE_COLUMN_LIST": {
        "description": "Use this when the response involves a list of items (e.g., top 5 movies, search results, recommended products).",
        "json": """
[
  {{ "beginRendering": {{ "surfaceId": "default", "root": "root-column", "styles": {{ "primaryColor": "#FF0000", "font": "Roboto" }} }} }},
  {{ "surfaceUpdate": {{
    "surfaceId": "default",
    "components": [
      {{ "id": "root-column", "component": {{ "Column": {{ "children": {{ "explicitList": ["title-heading", "item-list"] }} }} }} }},
      {{ "id": "title-heading", "component": {{ "Text": {{ "usageHint": "h1", "text": {{ "path": "title" }} }} }} }},
      {{ "id": "item-list", "component": {{ "List": {{ "direction": "vertical", "children": {{ "template": {{ "componentId": "item-card-template", "dataBinding": "/items" }} }} }} }} }},
      {{ "id": "item-card-template", "component": {{ "Card": {{ "child": "card-layout" }} }} }},
      {{ "id": "card-layout", "component": {{ "Row": {{ "children": {{ "explicitList": ["template-image", "card-details"] }} }} }} }},
      {{ "id": "template-image", "weight": 1, "component": {{ "Image": {{ "url": {{ "path": "imageUrl" }} }} }} }},
      {{ "id": "card-details", "weight": 2, "component": {{ "Column": {{ "children": {{ "explicitList": ["template-name", "template-detail"] }} }} }} }},
      {{ "id": "template-name", "component": {{ "Text": {{ "usageHint": "h3", "text": {{ "path": "name" }} }} }} }},
      {{ "id": "template-detail", "component": {{ "Text": {{ "text": {{ "path": "detail" }} }} }} }}
    ]
  }} }},
  {{ "dataModelUpdate": {{
    "surfaceId": "default",
    "path": "/",
    "contents": [
      {{ "key": "title", "valueString": "List Title" }},
      {{ "key": "items", "valueMap": [] }}
    ]
  }} }}
]
"""
    },
    "FORM": {
        "description": "Use this when you need to collect information from the user (e.g., sign up, survey, booking request).",
        "json": """
[
  {{ "beginRendering": {{ "surfaceId": "form-surface", "root": "form-column", "styles": {{ "primaryColor": "#0000FF", "font": "Roboto" }} }} }},
  {{ "surfaceUpdate": {{
    "surfaceId": "form-surface",
    "components": [
      {{ "id": "form-column", "component": {{ "Column": {{ "children": {{ "explicitList": ["form-title", "name-field", "email-field", "submit-button"] }} }} }} }},
      {{ "id": "form-title", "component": {{ "Text": {{ "usageHint": "h2", "text": {{ "path": "title" }} }} }} }},
      {{ "id": "name-field", "component": {{ "TextField": {{ "label": {{ "literalString": "Name" }}, "text": {{ "path": "userName" }} }} }} }},
      {{ "id": "email-field", "component": {{ "TextField": {{ "label": {{ "literalString": "Email" }}, "text": {{ "path": "userEmail" }} }} }} }},
      {{ "id": "submit-button", "component": {{ "Button": {{ "child": "submit-text", "primary": true, "action": {{ "name": "submit_form", "context": [ {{ "key": "name", "value": {{ "path": "userName" }} }}, {{ "key": "email", "value": {{ "path": "userEmail" }} }} ] }} }} }} }},
      {{ "id": "submit-text", "component": {{ "Text": {{ "text": {{ "literalString": "Submit" }} }} }} }}
    ]
  }} }},
  {{ "dataModelUpdate": {{
    "surfaceId": "form-surface",
    "path": "/",
    "contents": [
      {{ "key": "title", "valueString": "Form Title" }},
      {{ "key": "userName", "valueString": "" }},
      {{ "key": "userEmail", "valueString": "" }}
    ]
  }} }}
]
"""
    },

    "SIMPLE_MESSAGE": {
        "description": "Use this for simple text responses, answers to questions, jokes, or chit-chat where no complex UI is needed.",
        "json": """
[
  {{ "beginRendering": {{ "surfaceId": "main", "root": "root-column" }} }},
  {{ "surfaceUpdate": {{
    "surfaceId": "main",
    "components": [
      {{ "id": "root-column", "component": {{ "Column": {{ "children": {{ "explicitList": ["message-card"] }} }} }} }},
      {{ "id": "message-card", "component": {{ "Card": {{ "child": "message-text" }} }} }},
      {{ "id": "message-text", "component": {{ "Text": {{ "text": {{ "literal": "REPLACE_WITH_YOUR_TEXT_RESPONSE" }} }} }} }}
    ]
  }} }}
]
"""
    },
    "CONFIRMATION": {
        "description": "Use this when confirming an action or submission (e.g., 'Booking confirmed', 'Message sent').",
        "json": """
[
  {{ "beginRendering": {{ "surfaceId": "confirmation", "root": "confirm-card", "styles": {{ "primaryColor": "#00AA00", "font": "Roboto" }} }} }},
  {{ "surfaceUpdate": {{
    "surfaceId": "confirmation",
    "components": [
      {{ "id": "confirm-card", "component": {{ "Card": {{ "child": "confirm-column" }} }} }},
      {{ "id": "confirm-column", "component": {{ "Column": {{ "children": {{ "explicitList": ["confirm-title", "confirm-message", "divider", "close-button"] }} }} }} }},
      {{ "id": "confirm-title", "component": {{ "Text": {{ "usageHint": "h2", "text": {{ "path": "title" }} }} }} }},
      {{ "id": "confirm-message", "component": {{ "Text": {{ "text": {{ "path": "message" }} }} }} }},
      {{ "id": "divider", "component": {{ "Divider": {{}} }} }},
      {{ "id": "close-button", "component": {{ "Button": {{ "child": "close-text", "action": {{ "name": "close_confirmation", "context": [] }} }} }} }},
      {{ "id": "close-text", "component": {{ "Text": {{ "text": {{ "literalString": "Close" }} }} }} }}
    ]
  }} }},
  {{ "dataModelUpdate": {{
    "surfaceId": "confirmation",
    "path": "/",
    "contents": [
      {{ "key": "title", "valueString": "Success!" }},
      {{ "key": "message", "valueString": "Your action was completed." }}
    ]
  }} }}
]
"""
    },
    "WEATHER_FORECAST": {
        "description": "Use this when the user asks for weather information (e.g., 'weather in Tokyo', 'forecast for tomorrow').",
        "json": """
[
  {{ "beginRendering": {{ "surfaceId": "weather", "root": "weather-card", "styles": {{ "primaryColor": "#2196F3", "font": "Roboto" }} }} }},
  {{ "surfaceUpdate": {{
    "surfaceId": "weather",
    "components": [
      {{ "id": "weather-card", "component": {{ "Card": {{ "child": "weather-layout", "children": [] }} }} }},
      {{ "id": "weather-layout", "component": {{ "Column": {{ "children": {{ "explicitList": ["location-text", "current-row", "forecast-list"] }} }} }} }},
      {{ "id": "location-text", "component": {{ "Text": {{ "usageHint": "h2", "text": {{ "path": "location" }} }} }} }},
      {{ "id": "current-row", "component": {{ "Row": {{ "children": {{ "explicitList": ["icon-image", "temp-text", "condition-text"] }} }} }} }},
      {{ "id": "icon-image", "weight": 1, "component": {{ "Image": {{ "url": {{ "path": "iconUrl" }} }} }} }},
      {{ "id": "temp-text", "weight": 1, "component": {{ "Text": {{ "usageHint": "h1", "text": {{ "path": "temperature" }} }} }} }},
      {{ "id": "condition-text", "weight": 2, "component": {{ "Text": {{ "text": {{ "path": "condition" }} }} }} }},
      {{ "id": "forecast-list", "component": {{ "List": {{ "direction": "vertical", "children": {{ "template": {{ "componentId": "forecast-item", "dataBinding": "/forecast" }} }} }} }} }},
      {{ "id": "forecast-item", "component": {{ "Row": {{ "children": {{ "explicitList": ["day-text", "high-low-text"] }} }} }} }},
      {{ "id": "day-text", "weight": 1, "component": {{ "Text": {{ "text": {{ "path": "day" }} }} }} }},
      {{ "id": "high-low-text", "weight": 1, "component": {{ "Text": {{ "text": {{ "path": "highLow" }} }} }} }}
    ]
  }} }},
  {{ "dataModelUpdate": {{
    "surfaceId": "weather",
    "path": "/",
    "contents": [
      {{ "key": "location", "valueString": "San Francisco, CA" }},
      {{ "key": "iconUrl", "valueString": "https://ssl.gstatic.com/onebox/weather/64/sunny.png" }},
      {{ "key": "temperature", "valueString": "72°F" }},
      {{ "key": "condition", "valueString": "Sunny" }},
      {{ "key": "forecast", "valueMap": [] }}
    ]
  }} }}
]
"""
    },
    "ARTICLE_VIEW": {
        "description": "Use this for providing detailed information, news, encyclopedia entries, or explanations about a specific topic.",
        "json": """
[
  {{ "beginRendering": {{ "surfaceId": "article", "root": "article-column", "styles": {{ "primaryColor": "#333333", "font": "Georgia" }} }} }},
  {{ "surfaceUpdate": {{
    "surfaceId": "article",
    "components": [
      {{ "id": "article-column", "component": {{ "Column": {{ "children": {{ "explicitList": ["hero-image", "article-title", "author-text", "divider", "article-body"] }} }} }} }},
      {{ "id": "hero-image", "component": {{ "Image": {{ "url": {{ "path": "imageUrl" }} }} }} }},
      {{ "id": "article-title", "component": {{ "Text": {{ "usageHint": "h1", "text": {{ "path": "title" }} }} }} }},
      {{ "id": "author-text", "component": {{ "Text": {{ "text": {{ "path": "author" }} }} }} }},
      {{ "id": "divider", "component": {{ "Divider": {{}} }} }},
      {{ "id": "article-body", "component": {{ "Text": {{ "text": {{ "path": "body" }} }} }} }}
    ]
  }} }},
  {{ "dataModelUpdate": {{
    "surfaceId": "article",
    "path": "/",
    "contents": [
      {{ "key": "title", "valueString": "Article Title" }},
      {{ "key": "imageUrl", "valueString": "https://via.placeholder.com/600x300" }},
      {{ "key": "author", "valueString": "By Author Name" }},
      {{ "key": "body", "valueString": "Article content goes here..." }}
    ]
  }} }}
]
"""
    }
}
