import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hello_ai_os/ui/recovery_learning_panel.dart';

void main() {
  testWidgets('No Proposal', (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: RecoveryLearningPanel(
            adaptationProposal: null,
            onDecide: (_) {},
          ),
        ),
      ),
    );
    expect(find.text('System Status: Normal'), findsOneWidget);
  });

  testWidgets('Show Proposal', (WidgetTester tester) async {
    final proposal = {
      "reason": "Too many crashes",
      "action": "Increase Height",
    };

    bool? accepted;
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: RecoveryLearningPanel(
            adaptationProposal: proposal,
            onDecide: (val) => accepted = val,
          ),
        ),
      ),
    );

    expect(find.text('Adaptation Proposed'), findsOneWidget);
    expect(find.text('Reason: Too many crashes'), findsOneWidget);

    await tester.tap(find.text('Apply Update'));
    expect(accepted, true);
  });
}
