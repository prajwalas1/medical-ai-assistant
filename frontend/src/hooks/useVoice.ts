import { useRef, useState } from "react";
import {
  Room,
  RoomEvent,
  Track,
  type RemoteParticipant,
  type RemoteTrackPublication,
} from "livekit-client";

import { fetchLiveKitToken } from "../services/livekit";

type AgentState = "listening" | "thinking" | "speaking" | "idle";

export function useVoice() {
  const [callStarted, setCallStarted] = useState(false);
  const [agentState, setAgentState] = useState<AgentState>("idle");

  const roomRef = useRef<Room | null>(null);
  const audioElRef = useRef<HTMLAudioElement | null>(null);

  async function startCall(language: string = "en",sttProvider: string = "sarvam",llmProvider: string = "sarvam") {
    const { token, url } = await fetchLiveKitToken(language,sttProvider,llmProvider);

    const room = new Room();
    roomRef.current = room;

    // --- Play the agent's audio track ---
    room.on(
      RoomEvent.TrackSubscribed,
      (track, _publication: RemoteTrackPublication, participant: RemoteParticipant) => {
        if (track.kind === Track.Kind.Audio) {
          const el = track.attach() as HTMLAudioElement;
          audioElRef.current = el;
          document.body.appendChild(el);
          el.play().catch(() => {
            // Autoplay can be blocked until a user gesture; startCall is
            // itself triggered by the "Start Call" click, so this is rare.
          });
        }
        void participant;
      }
    );

    room.on(RoomEvent.TrackUnsubscribed, (track) => {
      track.detach().forEach((el) => el.remove());
    });

    // --- Agent state (listening / thinking / speaking) via participant attributes ---
    const readAgentState = (participant: RemoteParticipant) => {
      const state = participant.attributes?.["lk.agent.state"] as AgentState | undefined;
      if (state) setAgentState(state);
    };

    room.on(RoomEvent.ParticipantAttributesChanged, (_changed, participant) => {
      if ("attributes" in participant) readAgentState(participant as RemoteParticipant);
    });

    room.on(RoomEvent.ParticipantConnected, (participant) => {
      readAgentState(participant);
    });

    try {
      await room.connect(url, token);
      await room.localParticipant.setMicrophoneEnabled(true);
      setCallStarted(true);
    } catch (err) {
      console.error("Failed to start call:", err);
      room.disconnect();
      roomRef.current = null;
    }
  }

  function stopCall() {
    roomRef.current?.disconnect();
    roomRef.current = null;

    if (audioElRef.current) {
      audioElRef.current.remove();
      audioElRef.current = null;
    }

    setCallStarted(false);
    setAgentState("idle");
  }

  return {
    callStarted,
    isListening: agentState === "listening",
    isProcessing: agentState === "thinking",
    isSpeaking: agentState === "speaking",
    startCall,
    stopCall,
  };
}