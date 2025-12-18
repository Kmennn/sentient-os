import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hello_ai_os/ui/week_insights_page.dart';

void main() {
  testWidgets('WeekInsightsPage displays insights', (
    WidgetTester tester,
  ) async {
    final insights = ["Mondays are heavy.", "You defer tasks on Friday."];

    await tester.pumpWidget(
      MaterialApp(home: WeekInsightsPage(insights: insights)),
    );

    expect(find.text('Mondays are heavy.'), findsOneWidget);
    expect(find.text('You defer tasks on Friday.'), findsOneWidget);
    expect(find.byIcon(Icons.lightbulb), findsNWidgets(2));
  });

  testWidgets('WeekInsightsPage handles empty state', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(home: WeekInsightsPage(insights: [])),
    );

    expect(find.text('No significant patterns detected.'), findsOneWidget);
  });
}
