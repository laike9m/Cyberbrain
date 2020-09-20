import * as vscode from "vscode";

suite('Extension Test Suite', function() {
	this.timeout(6000);

	test('cat coding', (done) => {
		vscode.commands.executeCommand("cyberbrain.init");
		setTimeout(() => {
			done();
		}, 5000);
	});
});