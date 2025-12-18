import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hello_ai_os/ui/conflict_panel.dart';

void main() {
  testWidgets('Shows no conflicts message', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(body: ConflictPanel(conflicts: [])),
      ),
    );

    expect(find.text('No active conflicts.'), findsOneWidget);
  });

  testWidgets('Shows conflict list and controls for Owner', (
    WidgetTester tester,
  ) async {
    final conflict = ConflictItem(
      id: '1',
      description: 'Mission A conflicts with B',
      canOverride: true,
    );

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(body: ConflictPanel(conflicts: [conflict])),
      ),
    );

    expect(find.text('Mission A conflicts with B'), findsOneWidget);
    expect(find.text('Allow'), findsOneWidget); // Approve button
    expect(find.text('Reject'), findsOneWidget); // Reject button
  });

  testWidgets('Shows awaiting message for non-privileged', (
    WidgetTester tester,
  ) async {
    final conflict = ConflictItem(
      id: '1',
      description: 'Mission A conflicts with B',
      canOverride: false,
    );

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(body: ConflictPanel(conflicts: [conflict])),
      ),
    );

    expect(find.text('Allow'), findsNothing);
    expect(find.text('Awaiting Owner Resolution'), findsOneWidget);
  });
}
