"""
    Author: Anna Johnson
    Date:  07/11/2022
    Version: 1
    Description: Adjusts the style sheets of UI elements
"""

#TODO: Make Style sheet with classes

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
            font: {theme["Font-Secondary"]};
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

        *[cssClass~="nav"] {{

        }}
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
        font: {theme["Font-Secondary"]};
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

    navButtonStyle = f"""
        QPushButton {{
            color: {theme["Text"]};
            background-color: {theme["Alt-Background"]};
            border-radius: 1px;
            border-width: 0px;
            padding: 0px;
            margin: 0px;

        }}

        QPushButton:hover {{
            color: {theme["Background"]};
            background-color: {theme["Text"]};
        }}
    """

    labelStyle = f"""
        color: {theme["Text"]};
        font: {theme["Font-Primary"]};
        qproperty-alignment: AlignHCenter;
    """

    labelStyle2 = f"""
        color: {theme["Text"]};
        font: {theme["Font-Heading"]};
        qproperty-alignment: AlignHCenter;
    """

    tableStyle = f"""
        QTableWidget {{
            color: {theme["Text"]};
            background-color: {theme["Background"]};
            alternate-background-color: {theme["Alt-Background"]};
            border-color: {theme["Text"]};
            border-bottom:2px;
            font: {theme["Font-Primary"]};
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
        color: {theme["Text"]};
        font: {theme["Font-Heading"]};
    """

    themeDict = {
        "QPushButton": buttonStyle,
        "QLabel": labelStyle,
        "Label 2": labelStyle2,
        "Button 2": buttonStyle2,
        "QTableWidget": tableStyle,
        "QLineEdit": lineEditStyle,
        "Nav Button": navButtonStyle,
    }

    if type(element) == list:
        for item in element:
            if option == "B2":
                item.setStyleSheet(themeDict["Button 2"])
            # elif option == "B3":
            #     item.setStyleSheet(themeDict["Button 3"])
            elif option == "L2":
                item.setStyleSheet(themeDict["Label 2"])
            elif option == "NB":
                item.setStyleSheet(themeDict["Nav Button"])
            else:
                item.setStyleSheet(themeDict[item.__class__.__name__])
                
    else:
        element.setStyleSheet(themeDict[element.__class__.__name__])
