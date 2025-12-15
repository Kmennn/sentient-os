import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hello_ai_os/ui/robot_control_panel.dart';

void main() {
  testWidgets('RobotControlPanel UI Structure', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: Scaffold(body: RobotControlPanel())),
    );

    expect(find.text('Robot Control'), findsOneWidget);
    expect(find.text('SIMULATION'), findsOneWidget); // Default
    expect(find.text('EMERGENCY STOP'), findsOneWidget);
  });

  testWidgets('Mode Switching', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: Scaffold(body: RobotControlPanel())),
    );

    // Tap Change Mode -> DRY_RUN
    await tester.tap(find.text('Change Mode'));
    await tester.pump();
    expect(find.text('DRY_RUN'), findsOneWidget);

    // Tap again -> LIVE
    await tester.tap(find.text('Change Mode'));
    await tester.pump();
    expect(find.text('LIVE'), findsOneWidget);
  });

  testWidgets('E-Stop Functionality', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: Scaffold(body: RobotControlPanel())),
    );

    // Switch to LIVE
    await tester.tap(find.text('Change Mode'));
    await tester.tap(find.text('Change Mode'));
    expect(find.text('LIVE'), findsOneWidget);

    // Hit E-STOP
    await tester.tap(find.text('EMERGENCY STOP'));
    await tester.pump();

    // Should revert to SIMULATION
    expect(find.text('SIMULATION'), findsOneWidget);
    // Should show Reset button
    expect(find.text('Reset E-STOP'), findsOneWidget);
  });
}
