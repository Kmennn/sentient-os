import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hello_ai_os/ui/delegation_panel.dart';

void main() {
  testWidgets('Delegation Panel lists and revokes', (
    WidgetTester tester,
  ) async {
    bool revoked = false;

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: DelegationPanel(
            delegations: [DelegationInfo("Alice", "Bob", "Active")],
            onCreateDelegation: (a, b, c) {},
            onRevoke: (id) => revoked = true,
          ),
        ),
      ),
    );

    expect(find.text("Alice -> Bob"), findsOneWidget);
    await tester.tap(find.text("Revoke"));
    expect(revoked, isTrue);
  });

  testWidgets('Delegation Panel creation trigger', (WidgetTester tester) async {
    bool created = false;

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: DelegationPanel(
            delegations: [],
            onCreateDelegation: (a, b, c) => created = true,
            onRevoke: (_) {},
          ),
        ),
      ),
    );

    await tester.tap(find.text("Delegate Authority"));
    expect(created, isTrue);
  });
}
