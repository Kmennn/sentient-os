import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hello_ai_os/ui/mission_insights_panel.dart';

void main() {
  testWidgets('MissionInsightsPanel displays data correctly', (
    WidgetTester tester,
  ) async {
    final insights = {
      'success_rate': 0.75,
      'failure_reason': 'Obstruction',
      'suggestions': ['Delay 5s', 'Avoid Concurrency'],
    };

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(body: MissionInsightsPanel(insights: insights)),
      ),
    );

    expect(find.text("Mission Insights"), findsOneWidget);
    expect(find.text("Success Rate: 75.0%"), findsOneWidget);
    expect(find.text("Most Common Failure: Obstruction"), findsOneWidget);
    expect(find.text("• Delay 5s"), findsOneWidget);
    expect(find.text("• Avoid Concurrency"), findsOneWidget);
  });

  testWidgets('MissionInsightsPanel handles empty data', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(body: MissionInsightsPanel(insights: {})),
      ),
    );

    expect(find.text("No insights available."), findsOneWidget);
  });
}
