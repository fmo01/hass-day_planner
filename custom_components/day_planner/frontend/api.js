console.info("api");
export class DayPlannerApi {
  constructor(hass) {
    this.hass = hass;
  }

  setHass(hass) {
    this.hass = hass;
  }

  async getConfiguration() {
    return this.hass.callWS({
      type: "day_planner/get_configuration",
    });
  }

  async getCalendar(
    startDate,
    endDate
  ) {
    return this.hass.callWS({
      type: "day_planner/get_calendar",
      start_date: startDate,
      end_date: endDate,
    });
  }

  async updateScheduledMoment(
    dayTypeId,
    momentId,
    time
  ) {
    return this.hass.callWS({
      type:
        "day_planner/update_scheduled_moment",
      day_type_id: dayTypeId,
      moment_id: momentId,
      time,
    });
  }

  async updateDayType(
    dayTypeId,
    name
  ) {
    return this.hass.callWS({
      type:
        "day_planner/update_day_type",
      day_type_id: dayTypeId,
      name,
    });
  }

  async addDayType(
    dayTypeId,
    name
  ) {
    return this.hass.callWS({
      type: "day_planner/add_day_type",
      day_type_id: dayTypeId,
      name,
    });
  }

  async removeDayType(
    dayTypeId
  ) {
    return this.hass.callWS({
      type: "day_planner/remove_day_type",
      day_type_id: dayTypeId,
    });
  }
}  
