from dash import Dash, html, dcc, callback, Input, Output
from dash.dash_table.Format import Padding
import dash_mantine_components as dmc
from datetime import date

external_stylesheets = [
    'https://fonts.googleapis.com/css2?family=Barlow:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&family=Ubuntu+Condensed&display=swa'
]

app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = dmc.MantineProvider(
    theme={
        "colorScheme": "dark",
        "primaryColor": "teal",
        "fontFamily": "'Barlow', sans-serif"
    },
    children=dmc.AppShell(
        [
            dmc.AppShellNavbar(
                dmc.Stack(
                    gap="md",
                    style={"padding": "15px"},
                    children=[
                        # Logo Section
                        dmc.Image(
                            src="assets/images/logo.png",
                            h=70,
                            w="auto",
                            fit="contain",
                        ),
                        
                        dmc.Divider(color="gray"),
                        
                        # Período Section
                        dmc.Stack(
                            gap="xs",
                            children=[
                                dmc.Text("Período", fw=600, size="sm", c="white"),
                                dmc.DateInput(
                                    id="date-start",
                                    placeholder="01/07/2025",
                                    value=date(2025, 7, 1),
                                    style={"width": "100%"},
                                    valueFormat="DD/MM/YYYY",
                                ),
                                dmc.DateInput(
                                    id="date-end",
                                    placeholder="31/12/2025",
                                    value=date(2025, 12, 31),
                                    style={"width": "100%"},
                                    valueFormat="DD/MM/YYYY",
                                ),
                            ]
                        ),
                        
                        # Tipo de Cupom Section
                        dmc.Stack(
                            gap="xs",
                            children=[
                                dmc.Text("Tipo de Cupom", fw=600, size="sm", c="white"),
                                dmc.Checkbox(label="Cashback", color="teal", id="check-cashback"),
                                dmc.Checkbox(label="Desconto", color="teal", id="check-desconto"),
                                dmc.Checkbox(label="Produto", color="teal", id="check-produto"),
                            ]
                        ),
                        
                        dmc.Divider(color="gray"),
                        
                        # Localização Section
                        dmc.Stack(
                            gap="xs",
                            children=[
                                dmc.Text("Localização", fw=600, size="sm", c="white"),
                                dmc.Text("Estado", size="xs", c="gray"),
                                dmc.TextInput(
                                    id="input-estado",
                                    placeholder="SP",
                                    style={"width": "100%"}
                                ),
                                dmc.Text("Cidade", size="xs", c="gray"),
                                dmc.TextInput(
                                    id="input-cidade",
                                    placeholder="São Paulo",
                                    style={"width": "100%"}
                                ),
                                dmc.Text("Bairro", size="xs", c="gray"),
                                dmc.TextInput(
                                    id="input-bairro",
                                    placeholder="Liberdade",
                                    style={"width": "100%"}
                                ),
                            ]
                        ),
                        
                        # Buttons
                        dmc.Stack(
                            gap="xs",
                            style={"marginTop": "20px"},
                            children=[
                                dmc.Button(
                                    "Aplicar filtros",
                                    id="btn-apply",
                                    fullWidth=True,
                                    color="teal",
                                    variant="filled"
                                ),
                                dmc.Button(
                                    "Limpar filtros",
                                    id="btn-clear",
                                    fullWidth=True,
                                    color="teal",
                                    variant="outline"
                                ),
                            ]
                        ),
                        
                        # User
                        dmc.Flex(
                            children=[
                                dmc.ThemeIcon(
                                    # props as configured above:
                                    variant="filled",
                                    size="xl",
                                    radius="xl",
                                    color="white",
                                    # other props...
                                ),
                                dmc.Stack(
                                    children=[
                                        dmc.Text("Rodraigo", fw=600, size="xs", c="white"),
                                        dmc.Text("CEO", fw=600, size="xs", c="white")
                                    ]
                                ),
                                dmc.Button(
                                    "Sair",
                                    size="xs",
                                    variant="light",
                                    color="red",                               
                                )
                            ],
                            # props as configured above:
                            gap="xs",
                            justify="space-between",
                            align="center",
                            direction="row",
                            wrap="wrap",
                            # other props...
                        ),
                    ]
                ),
                classNames={"navbar": "dmc-navbar"}
            ),
            dmc.AppShellMain(
                dmc.Container(
                    fluid=True,
                    style={
                        "minHeight": "calc(100vh - 60px)",
                        "margin": "0",
                        "padding": "0"
                    },
                    children=[
                        # Main content area - currently empty as in the image
                        dmc.Stack(
                            children=[
                                dmc.Tabs(
                                    [
                                        dmc.TabsList(
                                            [
                                                dmc.TabsTab("Geral", value="geral"),
                                                dmc.TabsTab("CEO", value="ceo"),
                                                dmc.TabsTab("CFO", value="cfo"),
                                                dmc.TabsTab("Mapa de Cupons", value="mapa_de_cupons"),
                                                dmc.TabsTab("Mapa de Clientes", value="mapa_de_clientes"),
                                            ],
                                            # Tabs style props
                                            grow=True,
                                            justify="flex-start",
                                        ),
                                        dmc.TabsPanel("Content for geral" ,value="geral"),
                                        dmc.TabsPanel("Content for ceo" ,value="ceo"),
                                        dmc.TabsPanel("Content for cfo" ,value="cfo"),
                                        dmc.TabsPanel("Content for mapa de cupons" ,value="mapa_de_cupons"),
                                        dmc.TabsPanel("Content for mapa de clientes" ,value="mapa_de_clientes")
                                    ],
                                    value="geral",
                                    classNames={"tab": "dmc-tabs"}
                                ),
                                # Graficos
                                dmc.Container(
                                    
                                )
                            ]
                        )
                        # PicBot button (bottom right)
                        # dmc.Affix(
                        #     position={"bottom": 20, "right": 20},
                        #     children=dmc.ActionIcon(
                        #         size="xl",
                        #         radius="xl",
                        #         color="teal",
                        #         variant="filled",
                        #         children=[
                        #             dmc.Group(
                        #                 gap="xs",
                        #                 children=[
                        #                     dmc.Text("PicBot", size="sm", fw=500),
                        #                     dmc.Text("💬", size="lg"),
                        #                 ]
                        #             )
                        #         ],
                        #         style={"width": "auto", "padding": "10px 20px"}
                        #     )
                        # )
                    ]
                ),
                style={
                    
                    "backgroundColor": "#0d3d3d",
                },
            ),
        ],
        id="app-shell",
        navbar={"width": 250, "breakpoint": "sm"}
    )
)

if __name__ == '__main__':
    app.run(debug=True)
