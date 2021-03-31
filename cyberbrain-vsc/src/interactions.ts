import { window, Range, Position, workspace, TextEditor, OverviewRulerLane } from 'vscode'

export class Interactions {

    private decorationType = window.createTextEditorDecorationType({
            isWholeLine: true,
            overviewRulerColor: 'blue',
		    overviewRulerLane:  OverviewRulerLane.Right,
            light: {
                // this color will be used in light color themes
                backgroundColor: 'lightblue'
            },
            dark: {
                // this color will be used in dark color themes
                backgroundColor: 'darkblue'
            }
        });

    highlightLineOnEditor(lineno: number, relativePath: string) {

        const nodeEditor = window.visibleTextEditors.filter(
            editor => editor.document.uri.fsPath.indexOf(relativePath) !== -1)[0]
        if (nodeEditor) {
            let lineRange = [{ range: new Range(new Position(lineno, 0), new Position(lineno, 100)) }]
            nodeEditor.setDecorations(this.decorationType, lineRange)
        }
    }

    execute(context: { interactionType: String, info?: any }) {
        switch (context.interactionType) {
            case "Hover":
                if (context.info?.hasOwnProperty("lineno"))
                    this.highlightLineOnEditor(context.info["lineno"], context.info["relativePath"]);
                break;
            default:
                break;
        }
    }
}