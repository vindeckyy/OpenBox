import os
import tempfile
import time


def main():
    with tempfile.TemporaryDirectory() as directory:
        os.environ["OPENBOX_DATA_DIR"] = directory
        from openbox import save_state
        from web_app import RUNNING, control_game_session, start_game

        save_state({"games":[{"name":"Session test", "path":"/bin/sleep", "launch":"sleep 30"}], "profiles":{}, "history":[]})
        session = start_game(0)
        control_game_session(session["launch_id"], "pause")
        time.sleep(.03)
        assert "\nState:\tT" in open(f"/proc/{session['pid']}/status").read()
        control_game_session(session["launch_id"], "resume")
        control_game_session(session["launch_id"], "stop")
        for _ in range(100):
            if not RUNNING:
                break
            time.sleep(.01)
        assert not RUNNING
    print("session self-test: ok")


if __name__ == "__main__":
    main()
