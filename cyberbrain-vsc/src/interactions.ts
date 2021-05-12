import {
  OverviewRulerLane,
  Position,
  Range,
  TextEditorDecorationType,
  window
} from "vscode";

enum Behavior {
  Hover = "Hover",
  Unhover = "Unhover"
}

/**
 * `Interactions` is used to implement the interaction behaviors from users when they interact with cyberbrain webpages.
 * To add an interaction, post message to Vscode when a user's interaction behavior is detected, parse the message with rpc server,
 * define relative interactions logic in the `Interactions`, and then call `Interactions.execute` to execute it.
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
   * Highlight the given line on the Editor.
   * @param lineno  the highlighted line's number.
   * @param relativePath  the relative path of the file which the highlighted line belongs to.
   */
  highlightLineOnEditor(lineno: number, relativePath: string) {
    if (lineno < 0) {
      return;
    }
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

  execute(interactionConfig: { type: String; info?: any }) {
    switch (interactionConfig.type) {
      case Behavior.Hover:
        if (interactionConfig.info?.hasOwnProperty("lineno")) {
          this.highlightLineOnEditor(
            interactionConfig.info["lineno"],
            interactionConfig.info["relativePath"]
          );
        }
        break;
      case Behavior.Unhover:
        if (this.decorateType) {
          this.decorateType.dispose();
        }
        break;
      default:
        break;
    }
  }
}
