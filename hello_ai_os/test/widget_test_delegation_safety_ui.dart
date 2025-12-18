import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hello_ai_os/ui/delegation_panel.dart';

void main() {
  testWidgets('Delegation Panel shows safety warning at limit', (
    WidgetTester tester,
  ) async {
    // 3 Delegations
    final ds = [
      DelegationInfo("A", "B", "Active"),
      DelegationInfo("A", "C", "Active"),
      DelegationInfo("A", "D", "Active"),
    ];

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: DelegationPanel(
            delegations: ds,
            onCreateDelegation: (a, b, c) {},
            onRevoke: (_) {},
          ),
        ),
      ),
    );

    expect(find.text("Delegation limit reached (3/3)."), findsOneWidget);
  });
}
