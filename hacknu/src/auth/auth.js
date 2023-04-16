function createStorageEntity(key) {
  const get = () => {
    if (typeof window === "undefined") return null;

    const val = window.localStorage.getItem(key);

    if (val === null) return null;

    return JSON.parse(val);
  };

  const set = (value) => {
    if (typeof window === "undefined") return;

    return window.localStorage.setItem(key, JSON.stringify(value));
  };

  const remove = () => {
    if (typeof window === "undefined") return;

    return window.localStorage.removeItem(key);
  };

  return { get, set, remove };
}

const storage = createStorageEntity("ACCESS_TOKEN");
const isSignedIn = () => {
  const token = storage.get();

  return !!token;
};

let listeners = [];

const subscribe = (cb) => {
  const token = storage.get()?.value ?? null;

  cb(token);
  listeners.push(cb);

  return () => {
    listeners = listeners.filter((list) => list !== cb);
  };
};

const updateToken = (token) => {
  if (token === null) {
    storage.remove();
  } else {
    storage.set({ value: token });
  }
  listeners.forEach((cb) => cb(token));
};

export const auth = {
  isSignedIn,
  subscribe,
  updateToken,
};
