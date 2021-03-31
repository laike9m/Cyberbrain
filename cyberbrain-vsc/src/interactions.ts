import { window, Range, Position, workspace, TextEditor, OverviewRulerLane, TextEditorDecorationType } from 'vscode'

export class Interactions {

    private decorateType: TextEditorDecorationType | undefined;
    getDecorationType = function () {
        return window.createTextEditorDecorationType({
            isWholeLine: true,
            overviewRulerColor: 'blue',
            overviewRulerLane: OverviewRulerLane.Right,
            light: {
                // this color will be used in light color themes
                backgroundColor: 'lightblue'
            },
            dark: {
                // this color will be used in dark color themes
                backgroundColor: 'darkblue'
            }
        });
    }

    highlightLineOnEditor(lineno: number, relativePath: string) {

        const nodeEditor = window.visibleTextEditors.filter(
            editor => editor.document.uri.fsPath.indexOf(relativePath) !== -1)[0]
        if (nodeEditor) {
            // create a decoration type everytime since it will be disposed when unhovering the node
            this.decorateType = this.getDecorationType();
            let lineRange = [{ range: new Range(new Position(lineno - 1, 0), new Position(lineno - 1, 100)) }]
            nodeEditor.setDecorations(this.decorateType, lineRange)
        }
    }

    execute(context: { interactionType: String, info?: any }) {
        switch (context.interactionType) {
            case "Hover":
                if (context.info?.hasOwnProperty("lineno"))
                    this.highlightLineOnEditor(context.info["lineno"], context.info["relativePath"]);
                break;
            case "Unhover":
                if (this.decorateType) {
                    this.decorateType.dispose();
                }
                break;
            default:
                break;
        }
    }
}