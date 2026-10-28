export class DayPlannerApi {
  constructor(hass) {
    this.hass = hass;
  }

  setHass(hass) {
    this.hass = hass;
  }

  async getConfiguration() {
    return this.hass.callWS({
      type: 'day_planner/get_configuration',
    });
  }

  async getCalendar(startDate, endDate) {
    return this.hass.callWS({
      type: 'day_planner/get_calendar',
      start_date: startDate,
      end_date: endDate,
    });
  }

  async updateScheduledMoment(dayTypeId, momentId, time) {
    return this.hass.callWS({
      type: 'day_planner/update_scheduled_moment',
      day_type_id: dayTypeId,
      moment_id: momentId,
      time,
    });
  }

  async updateDayType(dayTypeId, name) {
    return this.hass.callWS({
      type: 'day_planner/update_day_type',
      day_type_id: dayTypeId,
      name,
    });
  }

  async addDayType(dayTypeId, name) {
    return this.hass.callWS({
      type: 'day_planner/add_day_type',
      day_type_id: dayTypeId,
      name,
    });
  }

  async addWeekSchedule(
    weekScheduleId,
    name,
    monday,
    tuesday,
    wednesday,
    thursday,
    friday,
    saturday,
    sunday
  ) {
    return this.hass.callWS({
      type: 'day_planner/add_week_schedule',
      week_schedule_id: weekScheduleId,
      name,
      monday,
      tuesday,
      wednesday,
      thursday,
      friday,
      saturday,
      sunday,
    });
  }

  async updateWeekSchedule(
    weekScheduleId,
    name,
    monday,
    tuesday,
    wednesday,
    thursday,
    friday,
    saturday,
    sunday
  ) {
    return this.hass.callWS({
      type: 'day_planner/update_week_schedule',
      week_schedule_id: weekScheduleId,
      name,
      monday,
      tuesday,
      wednesday,
      thursday,
      friday,
      saturday,
      sunday,
    });
  }

  async removeWeekSchedule(weekScheduleId) {
    return this.hass.callWS({
      type: 'day_planner/remove_week_schedule',
      week_schedule_id: weekScheduleId,
    });
  }

  async removeDayType(dayTypeId) {
    return this.hass.callWS({
      type: 'day_planner/remove_day_type',
      day_type_id: dayTypeId,
    });
  }

  async addScheduledMoment(dayTypeId, momentId, time) {
    return this.hass.callWS({
      type: 'day_planner/add_scheduled_moment',
      day_type_id: dayTypeId,
      moment_id: momentId,
      time,
    });
  }

  async removeScheduledMoment(dayTypeId, momentId) {
    return this.hass.callWS({
      type: 'day_planner/remove_scheduled_moment',
      day_type_id: dayTypeId,
      moment_id: momentId,
    });
  }

  async addCycle(cycleId, name, startDate, weekScheduleIds) {
    return this.hass.callWS({
      type: 'day_planner/add_cycle',
      cycle_id: cycleId,
      name,
      start_date: startDate,
      week_schedule_ids: weekScheduleIds,
    });
  }

  async updateCycle(cycleId, name, startDate, weekScheduleIds) {
    return this.hass.callWS({
      type: 'day_planner/update_cycle',
      cycle_id: cycleId,
      name,
      start_date: startDate,
      week_schedule_ids: weekScheduleIds,
    });
  }

  async removeCycle(cycleId) {
    return this.hass.callWS({
      type: 'day_planner/remove_cycle',
      cycle_id: cycleId,
    });
  }

  async addCalendarException(calendarExceptionId, date, dayTypeId, description = null) {
    return this.hass.callWS({
      type: 'day_planner/add_calendar_exception',
      calendar_exception_id: calendarExceptionId,
      date,
      day_type_id: dayTypeId,
      description,
    });
  }

  async updateCalendarException(calendarExceptionId, date, dayTypeId, description = null) {
    return this.hass.callWS({
      type: 'day_planner/update_calendar_exception',
      calendar_exception_id: calendarExceptionId,
      date,
      day_type_id: dayTypeId,
      description,
    });
  }

  async removeCalendarException(calendarExceptionId) {
    return this.hass.callWS({
      type: 'day_planner/remove_calendar_exception',
      calendar_exception_id: calendarExceptionId,
    });
  }

async addMomentAction(momentId, actionId, label, sequence) {
  return this.hass.callWS({
    type: 'day_planner/add_moment_action',
    moment_id: momentId,
    action_id: actionId,
    label,
    sequence,
  });
}

async updateMomentAction(momentId, actionId, label, sequence) {
  return this.hass.callWS({
    type: 'day_planner/update_moment_action',
    moment_id: momentId,
    action_id: actionId,
    label,
    sequence,
  });
}

async removeMomentAction(momentId, actionId) {
  return this.hass.callWS({
    type: 'day_planner/remove_moment_action',
    moment_id: momentId,
    action_id: actionId,
  });
}

async addMoment(momentId, name, icon = null) {
  return this.hass.callWS({
    type: 'day_planner/add_moment',
    moment_id: momentId,
    name,
    icon,
  });
}

async updateMoment(momentId, name, icon = null) {
  return this.hass.callWS({
    type: 'day_planner/update_moment',
    moment_id: momentId,
    name,
    icon,
  });
}

async removeMoment(momentId) {
  return this.hass.callWS({
    type: 'day_planner/remove_moment',
    moment_id: momentId,
  });
}

}

console.info(
  '%c API  %c v0.1.0',
  'color: orange; font-weight: bold; background: black',
  'color: white; font-weight: bold; background: dimgray'
);
