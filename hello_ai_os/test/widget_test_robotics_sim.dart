import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hello_ai_os/ui/robotics_sim_page.dart';

void main() {
  testWidgets('RoboticsSimPage structure', (WidgetTester tester) async {
    await tester.pumpWidget(const MaterialApp(home: RoboticsSimPage()));
    expect(find.text('Robotics Simulation'), findsOneWidget);
    expect(find.text('Arm Visualization Area'), findsOneWidget);
    expect(find.text('Execute Trajectory'), findsOneWidget);
    expect(find.text('SAFETY: Zone Clear'), findsOneWidget);
  });
}
