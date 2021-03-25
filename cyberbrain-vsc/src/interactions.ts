import { window, workspace} from 'vscode'

export class Interactions { 
    //let currentHightlightLineno = null;
    highlightLineOnEditor(lineno: Number) {
        // TODO: Implement line highlight function on Editor
    }

    
    execute(context: { interactionType: String, info?: any }) {
        switch (context.interactionType) {
            case "Hover":
                if (context.info?.hasOwnProperty("lineno"))
                    this.highlightLineOnEditor(context.info["lineno"]);
                break;
            default:
                break;
        }
    }
}