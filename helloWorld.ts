console.log('DEBUG_ Hello World!');

type MyUnion =
  | {
      kind: 'a';
      a: string;
    }
  | {
      kind: 'b';
      b: string;
    }
  | {
      kind: 'c';
      c: string;
    };

const derp = (myUnion: MyUnion): string => {
  switch (myUnion.kind) {
    case 'a':
      return myUnion.a;
    case 'b':
      return myUnion.b;
    case 'c':
      return myUnion.c;
  }
};
