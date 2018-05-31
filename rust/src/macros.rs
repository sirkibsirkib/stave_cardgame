
macro_rules! lex_iter {
	($e:expr, $f:expr, $g:expr) => {{
		$e.flat_map(
			move |x|
			$f.flat_map(
				move |y|
				$g.map(
					move |z|
					(x, y, z)
				)
			)
		)
	}};
	($e:expr, $f:expr) => {{
		$e.flat_map(
			move |x|
			$f.map(
				move |y|
				(x, y)
			)
		)
	}};
	($e:expr) => {{
		$e
	}};
	() => { iter::empty() };
}