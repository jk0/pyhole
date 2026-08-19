/* Copyright 2010-2026 Josh Kearney and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

#include "pyhole/hooks.h"
#include "pyhole/http.h"
#include "pyhole/util.h"

#include "../vendor/cJSON.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Minimal query-escape for a location string. */
static char *url_encode(const char *s)
{
    size_t cap = strlen(s) * 3 + 1;
    char *out = xmalloc(cap);
    size_t n = 0;
    for (; *s; s++) {
        unsigned char c = (unsigned char)*s;
        if ((c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') || (c >= '0' && c <= '9') || c == '-' ||
            c == '_' || c == '.' || c == '~') {
            out[n++] = (char)c;
        } else if (c == ' ') {
            out[n++] = '%';
            out[n++] = '2';
            out[n++] = '0';
        } else {
            n += (size_t)snprintf(out + n, cap - n, "%%%02X", c);
        }
    }
    out[n] = '\0';
    return out;
}

static void weather_work(Message *m, const char *location)
{
    char *q = url_encode(location);
    char url[768];
    snprintf(url, sizeof(url), "https://geocoding-api.open-meteo.com/v1/search?name=%s&count=1", q);
    free(q);
    HttpResponse *geo = http_get(url);
    if (geo == NULL || geo->body == NULL) {
        message_dispatch(m, "Unable to fetch weather data.");
        http_response_free(geo);
        return;
    }
    cJSON *root = cJSON_Parse(geo->body);
    http_response_free(geo);
    cJSON *results = root ? cJSON_GetObjectItemCaseSensitive(root, "results") : NULL;
    cJSON *place = results ? cJSON_GetArrayItem(results, 0) : NULL;
    if (place == NULL) {
        char buf[160];
        snprintf(buf, sizeof(buf), "Location not found: '%s'", location);
        message_dispatch(m, buf);
        cJSON_Delete(root);
        return;
    }
    cJSON *lat = cJSON_GetObjectItemCaseSensitive(place, "latitude");
    cJSON *lon = cJSON_GetObjectItemCaseSensitive(place, "longitude");
    cJSON *name = cJSON_GetObjectItemCaseSensitive(place, "name");
    cJSON *admin = cJSON_GetObjectItemCaseSensitive(place, "admin1");
    cJSON *cc = cJSON_GetObjectItemCaseSensitive(place, "country_code");
    if (!cJSON_IsNumber(lat) || !cJSON_IsNumber(lon)) {
        message_dispatch(m, "Unable to fetch weather data.");
        cJSON_Delete(root);
        return;
    }
    snprintf(url, sizeof(url),
             "https://api.open-meteo.com/v1/forecast?latitude=%f&longitude=%f"
             "&current_weather=true&windspeed_unit=mph&temperature_unit=fahrenheit",
             lat->valuedouble, lon->valuedouble);
    HttpResponse *fc = http_get(url);
    cJSON *froot = fc && fc->body ? cJSON_Parse(fc->body) : NULL;
    http_response_free(fc);
    cJSON *cur = froot ? cJSON_GetObjectItemCaseSensitive(froot, "current_weather") : NULL;
    cJSON *temp = cur ? cJSON_GetObjectItemCaseSensitive(cur, "temperature") : NULL;
    cJSON *wind = cur ? cJSON_GetObjectItemCaseSensitive(cur, "windspeed") : NULL;
    if (!cJSON_IsNumber(temp)) {
        message_dispatch(m, "Unable to fetch weather data.");
        cJSON_Delete(root);
        cJSON_Delete(froot);
        return;
    }
    char where[192] = "";
    if (cJSON_IsString(name)) {
        snprintf(where, sizeof(where), "%s", name->valuestring);
    }
    if (cJSON_IsString(admin) && admin->valuestring[0]) {
        size_t used = strlen(where);
        snprintf(where + used, sizeof(where) - used, ", %s", admin->valuestring);
    }
    if (cJSON_IsString(cc) && cc->valuestring[0]) {
        size_t used = strlen(where);
        snprintf(where + used, sizeof(where) - used, ", %s", cc->valuestring);
    }
    char buf[256];
    snprintf(buf, sizeof(buf), "%s: %.1f F   Wind: %.1f mph", where, temp->valuedouble,
             cJSON_IsNumber(wind) ? wind->valuedouble : 0.0);
    message_dispatch(m, buf);
    cJSON_Delete(root);
    cJSON_Delete(froot);
}

static void cmd_weather(Message *m, const char *params)
{
    if (params == NULL || *params == '\0') {
        message_dispatch(m, "Display current weather (ex: .w <location>).");
        return;
    }
    hook_spawn(weather_work, m, params);
}

static void cmd_w(Message *m, const char *params)
{
    cmd_weather(m, params);
}

void plugin_weather_register(void)
{
    hook_add_command("weather", cmd_weather, "Display current weather (ex: .w <location>).");
    hook_add_command("w", cmd_w, "Alias of weather.");
}
