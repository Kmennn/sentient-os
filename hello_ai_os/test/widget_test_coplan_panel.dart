import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hello_ai_os/ui/coplan_panel.dart';

void main() {
  testWidgets('CoPlanPanel shows Apply when Pending', (
    WidgetTester tester,
  ) async {
    bool applied = false;

    await tester.pumpWidget(
      MaterialApp(
        home: CoPlanPanel(
          proposalStatus: "PENDING",
          description: "Move Task A",
          onApply: () => applied = true,
          onUndo: () {},
          onCancel: () {},
        ),
      ),
    );

    expect(find.text("Apply Change"), findsOneWidget);
    await tester.tap(find.text("Apply Change"));
    expect(applied, isTrue);
  });

  testWidgets('CoPlanPanel shows Undo when Applied', (
    WidgetTester tester,
  ) async {
    bool undone = false;

    await tester.pumpWidget(
      MaterialApp(
        home: CoPlanPanel(
          proposalStatus: "APPLIED",
          description: "Move Task A",
          onApply: () {},
          onUndo: () => undone = true,
          onCancel: () {},
        ),
      ),
    );

    expect(find.text("Undo Change"), findsOneWidget);
    await tester.tap(find.text("Undo Change"));
    expect(undone, isTrue);
  });
}
