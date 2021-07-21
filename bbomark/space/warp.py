import numpy as np
from scipy.interpolate import interp1d
from scipy.special import expit as logistic  # because nobody calls it expit
from scipy.special import logit

# from bbomark.utils.util import clip_chk

WARPED_DTYPE = np.float_
N_GRID_DEFAULT = 8

def identity(x):
    """Helper function that perform warping in linear space. Sort of a no-op.

    Parameters
    ----------
    x : scalar
        Input variable in linear space. Can be any numeric type and is vectorizable.

    Returns
    -------
    y : scalar
        Same as input `x`.
    """
    y = x
    return y


def bilog(x):
    """Bilog warping function. Extension of log to work with negative numbers.

    ``Bilog(x) ~= log(x)`` for large `x` or ``-log(abs(x))`` if `x` is negative. However, the bias term ensures good
    behavior near 0 and ``bilog(0) = 0``.

    Parameters
    ----------
    x : scalar
        Input variable in linear space. Can be any numeric type and is vectorizable.

    Returns
    -------
    y : float
        The bilog of `x`.
    """
    y = np.sign(x) * np.log(1.0 + np.abs(x))
    return y


def biexp(x):
    """Inverse of :func:`.bilog` function.

    Parameters
    ----------
    x : scalar
        Input variable in linear space. Can be any numeric type and is vectorizable.

    Returns
    -------
    y : float
        The biexp of `x`.
    """
    y = np.sign(x) * (np.exp(np.abs(x)) - 1.0)
    return y


WARP_DICT = {"linear": identity, "log": np.log, "logit": logit, "bilog": bilog}
UNWARP_DICT = {"linear": identity, "log": np.exp, "logit": logistic, "bilog": biexp}

# def _error(msg, pre=False):  # pragma: validator
#     """Helper routine for :func:`.check_array`.
#
#     This could probably be made cleaner by using raise to create the assert.
#     """
#     if pre:
#         raise ValueError(msg)
#     else:
#         assert False, msg
#
# def check_array(
#     X,
#     name,
#     pre=False,
#     ndim=None,
#     shape=None,
#     shape_endswith=(),
#     min_size=0,
#     dtype=None,
#     kind=None,
#     allow_infinity=True,
#     allow_nan=True,
#     unsorted=True,
#     whitelist=None,
# ):  # pragma: validator
#     """Like :func:`sklearn:sklearn.utils.check_array` but better.
#
#     Check specified property of input array `X`. If an argument is not specified it passes by default.
#
#     Parameters
#     ----------
#     X : :class:`numpy:numpy.ndarray`
#         `numpy` array we want to validate.
#     name : str
#         Human readable name of of variable to refer to it in error messages. Note this can include spaces unlike simply
#         using the variable name.
#     pre : bool
#         If true, interpret this as check as validating pre-conditions to a function and will raise a `ValueError` if a
#         check fails. If false, assumes we are checking post-conditions and will raise an assertion failure.
#     ndim : int
#         Expected value of ``X.ndim``.
#     shape : tuple(int)
#         Expected value of ``X.shape``.
#     shape_endswith : tuple(int)
#         Expected that ``X.shape`` ends with `shape_endswith`. This is useful in broadcasting where extra dimensions
#         might be added on.
#     min_size : int
#         Minimum value for ``X.size``
#     dtype : dtype
#         Expected value of ``X.dtype``.
#     kind : str
#         Expected value of ``X.dtype.kind``. This is `'f'` for `float`, `'i'` for `int`, and so on.
#     allow_infinity : bool
#         If false, the check fails when `X` contains inf or ``-inf``.
#     allow_nan : bool
#         If false, the check fails when `X` contains a ``NaN``.
#     unsorted : bool
#         If false, the check fails when `X` is not in sorted order. This is designed to even work with string arrays.
#     whitelist : :class:`numpy:numpy.ndarray`
#         Array containing allowed values for `X`. If an element of `X` is not found in `whitelist`, the check fails.
#     """
#     if (ndim is not None) and X.ndim != ndim:
#         _error("Expected %d dimensions for %s, got %d" % (ndim, name, X.ndim), pre)
#
#     if (shape is not None) and X.shape != shape:
#         _error("Expected shape %s for %s, got %s" % (str(shape), name, str(X.shape)), pre)
#
#     if len(shape_endswith) > 0:
#         if X.shape[-len(shape_endswith) :] != shape_endswith:
#             if len(shape_endswith) == 1:
#                 _error("Expected shape (..., %d) for %s, got %s" % (shape_endswith[0], name, str(X.shape)), pre)
#             else:
#                 _error("Expected shape (..., %s for %s, got %s" % (str(shape_endswith)[1:], name, str(X.shape)), pre)
#
#     if (min_size > 0) and (X.size < min_size):
#         _error("%s needs at least %d elements, it has %d" % (name, min_size, X.size), pre)
#
#     if (dtype is not None) and X.dtype != np.dtype(dtype):
#         _error("Expected dtype %s for %s, got %s" % (str(np.dtype(dtype)), name, str(X.dtype)), pre)
#
#     if (kind is not None) and X.dtype.kind != kind:
#         _error("Expected array with kind %s for %s, got %s" % (kind, name, str(X.dtype.kind)), pre)
#
#     if (not allow_infinity) and np.any(np.abs(X) == np.inf):
#         _error("Infinity is not allowed in %s" % name, pre)
#
#     if (not allow_nan) and np.any(np.isnan(X)):
#         _error("NaN is not allowed in %s" % name, pre)
#
#     if whitelist is not None:
#         ok = np.all([xx in whitelist for xx in np.nditer(X, ["zerosize_ok"])])
#         if not ok:
#             _error("Expected all elements of %s to be in %s" % (name, str(whitelist)), pre)
#
#     # Only do this check in 1D
#     if X.ndim == 1 and (not unsorted) and np.any(X[:-1] > X[1:]):
#         _error("Expected sorted input for %s" % name, pre)


# class Warp(object):
#     """Base class for all types of variables.
#     """
#
#     def __init__(self, dtype=np.float_, default_round=identity, warp="linear", values=None, range_=None):
#         """Generic constructor of `Space` class.
#
#         Not intended to be called directly but instead by child classes. However, `Space` is not an abstract class and
#         will not give an error when instantiated.
#         """
#         self.dtype = dtype
#         assert warp in WARP_DICT, "invalid space %s, allowed spaces are: %s" % (str(warp), str(WARP_DICT.keys()))
#         self.warp_f = WARP_DICT[warp]
#         self.unwarp_f = UNWARP_DICT[warp]
#
#         # Setup range and rounding if values is suplied
#         assert (values is None) != (range_ is None)
#         round_to_values = default_round
#         if range_ is None:  # => value is not None
#             # Debatable if unique should be done before or after cast. But I
#             # think after is better, esp. when changing precisions.
#             values = np.asarray(values, dtype=dtype)
#             values = np.unique(values)  # values now 1D ndarray no matter what
#             check_array(
#                 values,
#                 "unique values",
#                 pre=True,
#                 ndim=1,
#                 dtype=dtype,
#                 min_size=2,
#                 allow_infinity=False,
#                 allow_nan=False,
#             )
#
#             # Extrapolation might happen due to numerics in type conversions.
#             # Bounds checking is still done in validate routines.
#             round_to_values = interp1d(values, values, kind="nearest", fill_value="extrapolate")
#             range_ = (values[0], values[-1])
#         # Save values and rounding
#         # Values is either None or was validated inside if statement
#         self.values = values
#         self.round_to_values = round_to_values
#
#         # Note that if dtype=None that is the default for asarray.
#         range_ = np.asarray(range_, dtype=dtype)
#         check_array(range_, "range", pre=True, shape=(2,), dtype=dtype, unsorted=False)
#         # Save range info, with input validation and post validation
#         self.lower, self.upper = range_
#
#         # Convert to warped bounds too with lots of post validation
#         self.lower_warped, self.upper_warped = self.warp_f(range_[..., None]).astype(WARPED_DTYPE, copy=False)
#         check_array(
#             self.lower_warped,
#             "warped lower bound %s(%.1f)" % (warp, self.lower),
#             ndim=1,
#             pre=True,
#             dtype=WARPED_DTYPE,
#             allow_infinity=False,
#             allow_nan=False,
#         )
#         # Should never happen if warpers are strictly monotonic:
#         assert np.all(self.lower_warped <= self.upper_warped)
#
#         # Make sure a bit bigger to keep away from lower due to numerics
#         self.upper_warped = np.maximum(self.upper_warped, np.nextafter(self.lower_warped, np.inf))
#         check_array(
#             self.upper_warped,
#             "warped upper bound %s(%.1f)" % (warp, self.upper),
#             pre=True,
#             shape=self.lower_warped.shape,
#             dtype=WARPED_DTYPE,
#             allow_infinity=False,
#             allow_nan=False,
#         )
#         # Should never happen if warpers are strictly monotonic:
#         assert np.all(self.lower_warped < self.upper_warped)
#
#     def validate(self, X, pre=False):
#         """Routine to validate inputs to warp.
#
#         This routine does not perform any checking on the dimensionality of `X` and is fully vectorized.
#         """
#         X = np.asarray(X, dtype=self.dtype)
#
#         if self.values is None:
#             X = clip_chk(X, self.lower, self.upper)
#         else:
#             check_array(X, "X", pre=pre, whitelist=self.values)
#
#         return X
#
#     def validate_warped(self, X, pre=False):
#         """Routine to validate inputs to unwarp. This routine is vectorized, but `X` must have at least 1-dimension.
#         """
#         X = np.asarray(X, dtype=WARPED_DTYPE)
#         check_array(X, "X", pre=pre, shape_endswith=(len(self.lower_warped),))
#
#         X = clip_chk(X, self.lower_warped, self.upper_warped)
#         return X
#
#     def warp(self, X):
#         """Warp inputs to a continuous space.
#
#         Parameters
#         ----------
#         X : :class:`numpy:numpy.ndarray` of shape (...)
#             Input variables to warp. This is vectorized to work in any dimension, but it must have the same type code
#             as the class, which is in `self.type_code`.
#
#         Returns
#         -------
#         X_w : :class:`numpy:numpy.ndarray` of shape (..., m)
#             Warped version of input space. By convention there is an extra dimension on warped array.
#             Currently, ``m=1`` for all warpers. `X_w` will have a `float` type.
#         """
#         X = self.validate(X, pre=True)
#
#         X_w = self.warp_f(X)
#         X_w = X_w[..., None]  # Convention is that warped has extra dim
#
#         X_w = self.validate_warped(X_w)  # Ensures of WAPRED_DTYPE
#         check_array(X_w, "X", ndim=X.ndim + 1, dtype=WARPED_DTYPE)
#         return X_w
#
#     def unwarp(self, X_w):
#         """Inverse of `warp` function.
#
#         Parameters
#         ----------
#         X_w : :class:`numpy:numpy.ndarray` of shape (..., m)
#             Warped version of input space. This is vectorized to work in any dimension. But, by convention, there is an
#             extra dimension on the warped array. Currently, the last dimension ``m=1`` for all warpers. `X_w` must be of
#             a `float` type.
#
#         Returns
#         -------
#         X : :class:`numpy:numpy.ndarray` of shape (...)
#             Unwarped version of `X_w`. `X` will have the same type code as the class, which is in `self.type_code`.
#         """
#         X_w = self.validate_warped(X_w, pre=True)
#
#         X = clip_chk(self.unwarp_f(X_w[..., 0]), self.lower, self.upper)
#         X = self.round_to_values(X)
#
#         X = self.validate(X)  # Ensures of dtype
#         check_array(X, "X", ndim=X_w.ndim - 1, dtype=self.dtype)
#         return X
#
#     def get_bounds(self):
#         """Get bounds of the warped space.
#
#         Returns
#         -------
#         bounds : :class:`numpy:numpy.ndarray` of shape (D, 2)
#             Bounds in the warped space. First column is the lower bound and the second column is the upper bound.
#             Calling ``bounds.tolist()`` gives the bounds in the standard form expected by `scipy` optimizers:
#             ``[(lower_1, upper_1), ..., (lower_n, upper_n)]``.
#         """
#         bounds = np.stack((self.lower_warped, self.upper_warped), axis=1)
#         check_array(bounds, "bounds", shape=(len(self.lower_warped), 2), dtype=WARPED_DTYPE)
#         return bounds
#
#     def grid(self, max_interp=N_GRID_DEFAULT):
#         """Return grid spanning the original (unwarped) space.
#
#         Parameters
#         ----------
#         max_interp : int
#             The number of points to use in grid space when a range and not values are used to define the space.
#             Must be ``>= 0``.
#
#         Returns
#         -------
#         values : list
#             Grid spanning the original space. This is simply `self.values` if a grid has already been specified,
#             otherwise it is just grid across the range.
#         """
#         values = self.values
#         if values is None:
#             vw = np.linspace(self.lower_warped, self.upper_warped, max_interp)
#             # Some spaces like int make result in duplicates after unwarping
#             # so we apply unique to avoid this. However this will usually be
#             # wasted computation.
#             values = np.unique(self.unwarp(vw[:, None]))
#             check_array(values, "values", ndim=1, dtype=self.dtype)
#
#         # Best to convert to list to make sure in native type
#         values = values.tolist()
#         return values
#
#
# class Real(Warp):
#     """Space for transforming real variables to normalized space (after warping).
#     """
#
#     def __init__(self, warp="linear", values=None, range_=None):
#         """Build Real space class.
#
#         Parameters
#         ----------
#         warp : {'linear', 'log', 'logit', 'bilog'}
#             Which warping type to apply to the space. The warping is applied in the original space. That is, in a space
#             with ``warp='log'`` and ``range_=(2.0, 10.0)``, the value 2.0 warps to ``log(2)``, not ``-inf`` as in some
#             other frameworks.
#         values : None or list(float)
#             Possible values for space to take. Values must be of `float` type.
#         range_ : None or :class:`numpy:numpy.ndarray` of shape (2,)
#             Array with (lower, upper) pair with limits of space. Note that one must specify `values` or `range_`, but
#             not both. `range_` must be composed of `float`.
#         """
#         assert warp is not None, "warp/space not specified for real"
#         super().__init__(np.float_, identity, warp, values, range_)
#
#
# class Integer(Warp):
#     """Space for transforming integer variables to continuous normalized space.
#     """
#
#     def __init__(self, warp="linear", values=None, range_=None):
#         """Build Integer space class.
#
#         Parameters
#         ----------
#         warp : {'linear', 'log', 'bilog'}
#             Which warping type to apply to the space. The warping is applied in the original space. That is, in a space
#             with ``warp='log'`` and ``range_=(2, 10)``, the value 2 warps to ``log(2)``, not ``-inf`` as in some other
#             frameworks. There are no settings with integers that are compatible with the logit warp.
#         values : None or list(float)
#             Possible values for space to take. Values must be of `int` type.
#         range_ : None or :class:`numpy:numpy.ndarray` of shape (2,)
#             Array with (lower, upper) pair with limits of space. Note that one must specify `values` or `range_`, but
#             not both. `range_` must be composed of `int`.
#         """
#         assert warp is not None, "warp/space not specified for int"
#         super().__init__(np.int_, np.round, warp, values, range_)
#
#
# class Boolean(Warp):
#     """Space for transforming Boolean variables to continuous normalized space.
#     """
#
#     def __init__(self, warp=None, values=None, range_=None):
#         """Build Boolean space class.
#
#         Parameters
#         ----------
#         warp : None
#             Must be omitted or None, provided for consitency with other types.
#         values : None
#             Must be omitted or None, provided for consitency with other types.
#         range_ : None
#             Must be omitted or None, provided for consitency with other types.
#         """
#         assert warp is None, "cannot warp bool"
#         assert (values is None) and (range_ is None), "cannot pass in values or range for bool"
#         self.dtype = np.bool_
#         self.warp_f = identity
#         self.unwarp_f = identity
#
#         self.values = np.array([False, True], dtype=np.bool_)
#         self.round_to_values = np.round
#
#         self.lower, self.upper = self.dtype(False), self.dtype(True)
#         self.lower_warped = np.array([0.0], dtype=WARPED_DTYPE)
#         self.upper_warped = np.array([1.0], dtype=WARPED_DTYPE)
#
#
# class Categorical(Warp):
#     """Space for transforming categorical variables to continuous normalized space.
#     """
#
#     def __init__(self, warp=None, values=None, range_=None):
#         """Build Integer space class.
#
#         Parameters
#         ----------
#         warp : None
#             Must be omitted or None, provided for consitency with other types.
#         values : list(str)
#             Possible values for space to take. Values must be unicode strings. Requiring type unicode (``'U'``) rather
#             than strings (``'S'``) corresponds to the native string type.
#         range_ : None
#             Must be omitted or None, provided for consitency with other types.
#         """
#         assert warp is None, "cannot warp cat"
#         assert values is not None, "must pass in explicit values for cat"
#         assert range_ is None, "cannot pass in range for cat"
#
#         values = np.unique(values)  # values now 1D ndarray no matter what
#         check_array(values, "values", pre=True, ndim=1, kind=CAT_KIND, min_size=2)
#         self.values = values
#
#         self.dtype = CAT_DTYPE
#         # Debatable if decode should go in unwarp or round_to_values
#
#         self.warp_f = self._encode
#         self.unwarp_f = identity
#         self.round_to_values = self._decode
#
#         self.lower, self.upper = None, None  # Don't need them
#         self.lower_warped = np.zeros(len(values), dtype=WARPED_DTYPE)
#         self.upper_warped = np.ones(len(values), dtype=WARPED_DTYPE)
#
#     def _encode(self, x):
#         return encode(x, self.values, True, WARPED_DTYPE, True)
#
#     def _decode(self, x):
#         return decode(x, self.values, True)
#
#     def warp(self, X):
#         """Warp inputs to a continuous space.
#
#         Parameters
#         ----------
#         X : :class:`numpy:numpy.ndarray` of shape (...)
#             Input variables to warp. This is vectorized to work in any dimension, but it must have the same
#             type code as the class, which is unicode (``'U'``) for the :class:`.Categorical` space.
#
#         Returns
#         -------
#         X_w : :class:`numpy:numpy.ndarray` of shape (..., m)
#             Warped version of input space. By convention there is an extra dimension on warped array. The warped space
#             has a one-hot encoding and therefore `m` is the number of possible values in the space. `X_w` will have
#             a `float` type.
#         """
#         X = self.validate(X, pre=True)
#
#         X_w = self.warp_f(X)
#
#         # Probably over kill to validate here too, but why not:
#         X_w = self.validate_warped(X_w)
#         check_array(X_w, "X", ndim=X.ndim + 1, dtype=WARPED_DTYPE)
#         return X_w
#
#     def unwarp(self, X_w):
#         """Inverse of `warp` function.
#
#         Parameters
#         ----------
#         X_w : :class:`numpy:numpy.ndarray` of shape (..., m)
#             Warped version of input space. The warped space has a one-hot encoding and therefore `m` is the number of
#             possible values in the space. `X_w` will have a `float` type. Non-zero/one values are allowed in `X_w`.
#             The maximal element in the vector is taken as the encoded value.
#
#         Returns
#         -------
#         X : :class:`numpy:numpy.ndarray` of shape (...)
#             Unwarped version of `X_w`. `X` will have same type code as the :class:`.Categorical` class, which is
#             unicode (``'U'``).
#         """
#         X_w = self.validate_warped(X_w, pre=True)
#
#         X = self.round_to_values(self.unwarp_f(X_w))
#
#         X = self.validate(X)
#         check_array(X, "X", ndim=X_w.ndim - 1, kind=CAT_KIND)
#         return X

