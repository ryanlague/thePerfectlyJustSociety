import plotly.graph_objects as go


def make_progress_graph(progress, total):
    progress_graph = (
        go.Figure(data=[go.Bar(x=[progress])],
                  layout=dict(title='Progress', titlefont={'size': 8, 'family': 'PlayfairDisplay-Regular'},
                              title_y=0.68, title_x=0.07, height=75, width=500, margin=dict(t=20, b=40),
                              paper_bgcolor='rgba(255, 255, 255, 0.0)'))
        .update_xaxes(range=[0, total])
        .update_yaxes(
            showticklabels=False
        )
    )
    return progress_graph
