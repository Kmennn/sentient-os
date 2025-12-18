import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hello_ai_os/ui/shared_coplan_panel.dart';

void main() {
  testWidgets('Shared Panel allows voting', (WidgetTester tester) async {
    bool voted = false;

    await tester.pumpWidget(
      MaterialApp(
        home: SharedCoPlanPanel(
          description: "Move Task",
          approvers: [Approver("Alice", "WAITING")],
          onVote: (v) => voted = v,
        ),
      ),
    );

    expect(find.text("Approve"), findsOneWidget);
    await tester.tap(find.text("Approve"));
    expect(voted, isTrue);
  });

  testWidgets('Shared Panel shows veto state and override', (
    WidgetTester tester,
  ) async {
    bool overridden = false;

    await tester.pumpWidget(
      MaterialApp(
        home: SharedCoPlanPanel(
          description: "Move Task",
          approvers: [Approver("Bob", "VETOED")],
          onVote: (_) {},
          canOverride: true,
          onOverride: () => overridden = true,
        ),
      ),
    );

    expect(find.text("Vetoed! Execution Paused."), findsOneWidget);
    expect(find.text("Override Veto (Admin)"), findsOneWidget);

    await tester.tap(find.text("Override Veto (Admin)"));
    expect(overridden, isTrue);
  });
}
