import {
  window,
  Range,
  Position,
  workspace,
  TextEditor,
  OverviewRulerLane,
  TextEditorDecorationType
} from "vscode";

enum Behaviors {
  Hover = "Hover",
  Unhover = "Unhover"
}

/**
 * `Interactions` is used to realize and manage the interaction behaviors from users when they iteract with the cyberbrain webpage.
 * To design a interation, post message to Vscode when a User's interaction behavior is detected, parse the message with rpc server,
 * define relative interactions logic in the `Interactions`, and then call `Interactions.excute` to excute it.
 * Current Interaction Behaviors includes:
 * 1. Highlight the line of the node in the editor when hovering the mouse on any node. Cancel the highlight when the node is unhovered.
 **/
export class Interactions {
  private decorateType: TextEditorDecorationType | undefined;

  getDecorationType(): TextEditorDecorationType {
    return window.createTextEditorDecorationType({
      isWholeLine: true,
      overviewRulerLane: OverviewRulerLane.Right,
      light: {
        // this color will be used in light color themes
        backgroundColor: "#fcf29f",
        overviewRulerColor: "#fcf29f"
      },
      dark: {
        // this color will be used in dark color themes
        backgroundColor: "#264F78",
        overviewRulerColor: "#264F78"
      }
    });
  }

  /**
   * Highlight the given line on the Editor
   * @param lineno  the highlighted line's number.
   * @param relativePath  the relative file path of the highlighted line
   */
  highlightLineOnEditor(lineno: number, relativePath: string) {
    const nodeEditor = window.visibleTextEditors.filter(
      editor => editor.document.uri.fsPath.indexOf(relativePath) !== -1
    )[0];
    if (nodeEditor) {
      // create a decoration type everytime since it will be disposed when unhovering the node
      this.decorateType = this.getDecorationType();
      let lineRange = [
        {
          range: new Range(
            new Position(lineno - 1, 0),
            new Position(lineno - 1, 100)
          )
        }
      ];
      nodeEditor.setDecorations(this.decorateType, lineRange);
    }
  }

  execute(context: { interactionType: String; info?: any }) {
    switch (context.interactionType) {
      case Behaviors.Hover:
        if (context.info?.hasOwnProperty("lineno")) {
          this.highlightLineOnEditor(
            context.info["lineno"],
            context.info["relativePath"]
          );
        }
        break;
      case Behaviors.Unhover:
        if (this.decorateType) {
          this.decorateType.dispose();
        }
        break;
      default:
        break;
    }
  }
}
