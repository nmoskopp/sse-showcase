import { EventSource } from "extended-eventsource";

// this is intended to fail (no credentials)
const eventSource_0 = new EventSource("/events");

// this works thanks to extended-eventsource
const eventSource_1 = new EventSource(
    "/events",
    {
        headers: {
            Authorization: "Bearer FooBar"
        }
    }
);

eventSource_0.onmessage = eventSource_1.onmessage = (event) => {
    console.log(`message ${event.lastEventId}: ${event.data}`);
};
