import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hello_ai_os/ui/day_overview_page.dart';

void main() {
  testWidgets('DayOverviewPage displays routines and tasks', (
    WidgetTester tester,
  ) async {
    final items = [
      {
        'id': 'r1',
        'type': 'ROUTINE',
        'name': 'Morning Focus',
        'start_seconds': 32400,
        'duration_seconds': 3600,
        'warnings': [],
      },
      {
        'id': 't1',
        'type': 'TASK',
        'name': 'Deploy App',
        'start_seconds': 36000,
        'duration_seconds': 1800,
        'warnings': ['Overlaps with break'],
      },
    ];

    await tester.pumpWidget(
      MaterialApp(home: DayOverviewPage(planItems: items)),
    );

    expect(find.text('Morning Focus'), findsOneWidget);
    expect(find.text('09:00'), findsOneWidget);
    expect(find.text('Deploy App'), findsOneWidget);
    expect(find.text('10:00'), findsOneWidget);
    expect(find.text('⚠️ Overlaps with break'), findsOneWidget);
  });
}
