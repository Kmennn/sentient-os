import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hello_ai_os/ui/policy_advisory_panel.dart';

void main() {
  testWidgets('Advisory Card Visualization', (WidgetTester tester) async {
    final suggestion = {
      "id": "123",
      "parameter": "lift_height",
      "delta": 0.1,
      "reason": "Sim says higher is safer",
    };

    var approvedId = "";

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: PolicyAdvisoryPanel(
            pendingSuggestion: suggestion,
            onApprove: (id) => approvedId = id,
            onReject: (_) {},
          ),
        ),
      ),
    );

    expect(find.text('Suggestion: Adjust lift_height'), findsOneWidget);
    expect(find.text('+0.1'), findsOneWidget);

    await tester.tap(find.text('APPROVE'));
    expect(approvedId, "123");
  });
}
