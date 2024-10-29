import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import json
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash import callback_context as ctx
from dash import Dash, dcc, html, Input, Output, State, callback_context
import numpy as np
import plotly.graph_objects as go

# Initialize the Dash app
app = dash.Dash(__name__)

# Function to load the JSON file
def load_events():
    with open('output.json', 'r') as file:
        return json.load(file)

# Function to save the JSON file
def save_events(events_data):
    with open('output.json', 'w') as file:
        json.dump(events_data, file, indent=4)

# Load the initial JSON file
events_data = load_events()

def create_plotly_figure(event, events_data):
    data = events_data[event][2]

    # Calculate statistics
    mean = np.mean(data)
    std_dev = np.std(data)
    min_val = np.min(data)
    max_val = np.max(data)

    # Create the plot
    fig = go.Figure()

    # Add a light vertical line to connect min and max
    fig.add_trace(go.Scatter(
        x=[0, 0], y=[min_val, max_val],
        mode='lines',
        line=dict(color='gray', width=1, dash='dash'),
        showlegend=False
    ))

    # Add error bars for standard deviation
    fig.add_trace(go.Scatter(
        x=[0], y=[mean],
        error_y=dict(type='data', array=[std_dev], visible=True),
        mode='markers',
        marker=dict(color='blue', size=10),
        name='Mean ± Std Dev'
    ))

    # Add markers for min and max
    fig.add_trace(go.Scatter(
        x=[0, 0], y=[min_val, max_val],
        mode='markers',
        marker=dict(color='red', size=20, symbol='line-ns'),
        name='Min/Max'
    ))

    # Add a red square marker at the last element of the data list
    fig.add_trace(go.Scatter(
        x=[0], y=[data[-1]],
        mode='markers',
        marker=dict(color='red', size=10, symbol='square'),
        name='Your guess'
    ))

    # Customize the plot
    fig.update_layout(
        title=event,
        yaxis_title='Value',
        xaxis_title='',
        xaxis=dict(showticklabels=False),
        yaxis=dict(range=[0, 1]),
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        width=600,  # Set the width of the graph
        height=800  # Set the height of the graph
    )

    return fig



# Define the layout of the app
app.layout = html.Div([
    html.H1('Event Probability Dashboard', style={'fontSize': '30px'}),
    
    dcc.Dropdown(
        id='event-dropdown',
        options=[{'label': k, 'value': k} for k in events_data.keys()],
        value=list(events_data.keys())[0] if events_data else None,
        style={'width': '50%', 'fontSize': '20px'}
    ),
    
    html.Div(id='event-output', style={'margin-top': '40px', 'fontSize': '18px'}),
    
    html.Div([
        dcc.Input(id='probability-input', type='number', placeholder='Enter probability (0-1)', min=0, max=1, step=0.01),
        html.Button('Add Probability', id='add-probability-button', n_clicks=0)
    ], id='probability-input-div', style={'display': 'none', 'margin-top': '15px', 'fontSize': '18px'}),
    
    html.H1('Create New Event'),
    html.H3('(e.g.  Interest rates will rise, |  the 10 year bond will be above 5%,  |  by 12/31/2024'),
    dcc.Input(id='new-event-name', type='text', placeholder='New Event Name', style={'margin-right': '20px', 'fontSize': '16px'}),
    dcc.Input(id='new-event-state', type='text', placeholder='State or Condition', style={'margin-right': '20px', 'fontSize': '16px'}),
    dcc.Input(id='new-event-when', type='text', placeholder='By When'),
    html.Button('Create New Event', id='new-event-button', n_clicks=0, style={'margin-top': '20px', 'fontSize': '16px'}),
    html.Div(id='new-event-output', style={'margin-top': '20px', 'fontSize': '16px'}),
    
    # Add this new Div for the graph
    html.Div(id='graph-container', style={'margin-top': '20px', 'width': '50%'})
])

# Callback to update the event output and show/hide probability input
@app.callback(
    [Output('event-output', 'children'),
     Output('probability-input', 'value'),
     Output('probability-input-div', 'style'),
     Output('graph-container', 'children')],
    [Input('event-dropdown', 'value'),
     Input('add-probability-button', 'n_clicks')],
    [State('probability-input', 'value')]
)
def update_event_and_probability(selected_event, n_clicks, probability):
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    graph = dash.no_update  # Default value for the graph

    if triggered_id == 'event-dropdown':
        if selected_event in events_data:
            event_info = events_data[selected_event]
            probabilities = ', '.join(map(str, event_info[2])) if event_info[2] else 'None'
            return (
                f"Event: {selected_event}\nState: {event_info[0]}\nBy When: {event_info[1]}",
                None,
                {'display': 'block', 'margin-top': '10px'},
                graph
            )
        return "Please select an event", None, {'display': 'none'}, graph
    
    elif triggered_id == 'add-probability-button':
        if n_clicks > 0 and selected_event and probability is not None:
            events_data[selected_event][2].append(float(probability))
            save_events(events_data)
            event_info = events_data[selected_event]
            probabilities = ', '.join(map(str, event_info[2]))
            
            # Create the graph
            fig = create_plotly_figure(selected_event, events_data)
            graph = dcc.Graph(figure=fig)
            
            return (
                f"Event: {selected_event}   State: {event_info[0]}   By When: {event_info[1]}",
                None,
                {'display': 'block', 'margin-top': '20px'},
                graph
            )
    
    # Default return if no condition is met
    return dash.no_update, dash.no_update, dash.no_update, graph

# Callback for the new event button
@app.callback(
    [Output('new-event-output', 'children'),
     Output('event-dropdown', 'options'),
     Output('new-event-name', 'value'),
     Output('new-event-state', 'value'),
     Output('new-event-when', 'value')],
    [Input('new-event-button', 'n_clicks')],
    [State('new-event-name', 'value'),
     State('new-event-state', 'value'),
     State('new-event-when', 'value')]
)
def create_new_event(n_clicks, new_name, new_state, new_when):
    if n_clicks > 0 and new_name and new_state and new_when:
        events_data[new_name] = [new_state, new_when, []]  # Added empty list for probabilities
        save_events(events_data)
        options = [{'label': k, 'value': k} for k in events_data.keys()]
        return f"New event '{new_name}' created successfully!", options, '', '', ''
    elif n_clicks > 0:
        return "Please fill in all fields for the new event.", [{'label': k, 'value': k} for k in events_data.keys()], '', '', ''
    return "", [{'label': k, 'value': k} for k in events_data.keys()], '', '', ''

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
