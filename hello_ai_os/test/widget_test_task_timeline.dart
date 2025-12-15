import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hello_ai_os/ui/task_timeline_panel.dart';

void main() {
  testWidgets('Timeline Visualization', (WidgetTester tester) async {
    final steps = [
      {"id": "1", "label": "Pick Cup", "status": "completed"},
      {"id": "2", "label": "Move Cup", "status": "active"},
      {"id": "3", "label": "Place Cup", "status": "pending"},
    ];

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(body: TaskTimelinePanel(steps: steps)),
      ),
    );

    expect(find.text('Pick Cup'), findsOneWidget);
    expect(find.byIcon(Icons.check_circle), findsOneWidget); // Completed
    expect(find.byIcon(Icons.motion_photos_on), findsOneWidget); // Active
  });

  testWidgets('Failure Indication', (WidgetTester tester) async {
    final steps = [
      {"id": "1", "label": "Pick", "status": "failed"},
    ];

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: TaskTimelinePanel(
            steps: steps,
            failureReason: "Gripper Jammed",
          ),
        ),
      ),
    );

    expect(find.text('Gripper Jammed'), findsOneWidget);
    expect(find.byIcon(Icons.error), findsOneWidget);
  });
}
