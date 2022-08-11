"""
    Author: Anna Johnson
    Date:  07/11/2022
    Version: 1
    Description: Adjusts the style sheets of UI elements
"""

import json, os, codecs

currentDir = os.getcwd()

def importTheme(style):
    with open("./resources/theme.JSON") as f:
        themes = json.load(f)
    theme = themes[style]
    return theme

def changeTheme(style, element, option =""):
    theme=importTheme(style)

    buttonStyle = f"""
        QPushButton {{
            color: {theme["Text"]};
            background-color: {theme["Background"]};
            padding: 5px;
            border-color: {theme["Alt-Background"]} {theme["Alt-Background"]} {theme["Highlight"]} {theme["Alt-Background"]};
            border-width:2px;
            border-radius: 5px;
            border-style: ridge;
            font: 12pt "Century Gothic";
        }}

        QPushButton:hover {{
            color: {theme["Alt-Background"]};
            background-color: {theme["Highlight"]};
            padding: 5px;
            border-color:{theme["Highlight"]} {theme["Highlight"]} {theme["Text"]} {theme["Highlight"]};
            border-width:2px;
            border-radius: 5px;
            border-style: ridge;
        }}
    """
    # TODO: add variables
    labelStyle = """
        color: rgb(230, 230, 230);
        font: 14pt "Century Gothic";
        qproperty-alignment: AlignHCenter;
    """

    labelStyle2 = """
        color: rgb(230, 230, 230);
        font: 25pt "Bebas Neue";
        qproperty-alignment: AlignHCenter;
    """

    buttonStyle2 = f"""
        QPushButton {{
        color: {theme["Text"]};
        background-color: {theme["Alt-Background"]};
        padding: 5px;
        border-color: {theme["Alt-Background"]} {theme["Alt-Background"]} {theme["Text"]} {theme["Alt-Background"]};
        border-width:2px;
        border-radius: 5px;
        border-style: ridge;
        font: 12pt "Century Gothic";
        }}

        QPushButton:hover {{
            color: {theme["Background"]};
            background-color: {theme["Text"]};
            padding: 5px;
            border-color:{theme["Text"]} {theme["Text"]} {theme["Alt-Background"]} {theme["Text"]};
            border-width:2px;
            border-radius: 5px;
            border-style: ridge;
        }}
    """
    tableStyle = f"""
        QTableWidget {{
            color: {theme["Text"]};
            background-color: {theme["Background"]};
            alternate-background-color: {theme["Alt-Background"]};
            border-color: {theme["Text"]};
            border-bottom:2px;
            font: 12pt "Century Gothic";
        }}

        QHeaderView::section {{
            color: {theme["Alt-Background"]};
            background-color: {theme["Highlight"]};
        }}

        CurrentCell::hover {{
            color: {theme["Alt-Background"]};
            background-color: {theme["Text"]}
        }}
    """

    lineEditStyle = f"""
        color: rgb(230, 230, 230);
        font: 25pt "Bebas Neue";

    """

    themeDict = {
        "QPushButton": buttonStyle,
        "QLabel": labelStyle,
        "Label 2": labelStyle2,
        "Button 2": buttonStyle2,
        "QTableWidget": tableStyle,
        "QLineEdit": lineEditStyle
    }

    if type(element) == list:
        for item in element:
            if option == "B2":
                item.setStyleSheet(themeDict["Button 2"])
            # elif option == "B3":
            #     item.setStyleSheet(themeDict["Button 3"])
            elif option == "L2":
                item.setStyleSheet(themeDict["Label 2"])
            else:
                item.setStyleSheet(themeDict[item.__class__.__name__])
                
    else:
        element.setStyleSheet(themeDict[element.__class__.__name__])
        # print(themeDict[element.__class__.__name__])
