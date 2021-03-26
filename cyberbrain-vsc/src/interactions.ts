import { window, Range, Position, workspace } from 'vscode'

export class Interactions {

    // TODO: beautify the highlight UI
    private decorationType = window.createTextEditorDecorationType({
        backgroundColor: 'yellow',
        border: '2px solid white',
    })

    highlightLineOnEditor(lineno: number, relativePath: string) {

        const nodeEditor = window.visibleTextEditors.filter(
            editor => editor.document.uri.fsPath.indexOf(relativePath) !== -1)[0]
        if (nodeEditor) {
            //TODO: The Range offset seems doesn't work. Whatever the range is, whole text part on the line will be highlighted. 
            // Maybe only highlight the variable? or use other way? Will improve it later.
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